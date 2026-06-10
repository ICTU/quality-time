"""Model transformations."""

import json
from json.decoder import JSONDecodeError
from typing import cast, TYPE_CHECKING

from shared.model.iterators import sources
from shared.model.source import LOCATION_PARAMETERS
from shared_data_model import DATA_MODEL

from utils.functions import asymmetric_decrypt, asymmetric_encrypt, uuid, DecryptionError

from .iterators import credential_holders

if TYPE_CHECKING:
    from shared.utils.type import ItemId

    from utils.type import SourceContext


CREDENTIALS_REPLACEMENT_TEXT = "this string replaces credentials"

# Source types without location parameters don't use source locations:
SOURCE_TYPES_WITHOUT_LOCATION = frozenset(
    source_type for source_type, source in DATA_MODEL.sources.items() if "url" not in source.parameters
)


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports. The data model must be passed so hiding also works when time traveling."""
    for parameters, keys in credential_holders(*reports, data_model=data_model):
        for key in keys:
            parameters[key] = CREDENTIALS_REPLACEMENT_TEXT


def encrypt_credentials(public_key: str, *reports: dict) -> None:
    """Encrypt all credentials in the reports."""
    for parameters, keys in credential_holders(*reports):
        for key in keys:
            value = parameters[key]
            if isinstance(value, dict | list):
                value = json.dumps(value)
            parameters[key] = asymmetric_encrypt(public_key, value)


def decrypt_credentials(private_key: str, *reports: dict) -> bool:
    """Decrypt all credentials in the reports. Returns whether all decryptions were successful."""
    decryption_successful = True
    for parameters, keys in credential_holders(*reports):
        for key in keys:
            decryption_successful &= decrypt_parameter(private_key, parameters, key)
    return decryption_successful


def decrypt_parameter(private_key: str, parameters: dict[str, str | tuple[str, str]], parameter_key: str) -> bool:
    """Decrypt a parameter. Returns whether the decryption was successful."""
    try:
        parameters[parameter_key] = decrypt_credential(private_key, parameters[parameter_key])
    except DecryptionError:
        del parameters[parameter_key]
        return False
    return True


def decrypt_credential(private_key: str, credential: str | tuple[str, str]) -> str | tuple[str, str]:
    """Decrypt the credential if it's encrypted, otherwise return it unchanged."""
    if isinstance(credential, str):
        return credential
    try:
        decrypted_credential = asymmetric_decrypt(private_key, credential)
    except ValueError as error:
        raise DecryptionError from error
    try:
        return cast(tuple[str, str], json.loads(decrypted_credential))
    except JSONDecodeError:
        return decrypted_credential


def replace_report_uuids(*reports) -> None:
    """Change all uuids in this report."""
    for report in reports:
        report["report_uuid"] = uuid()
        new_location_uuids = {location_uuid: uuid() for location_uuid in report.get("source_locations", {})}
        report["source_locations"] = {
            new_location_uuids[location_uuid]: location
            for location_uuid, location in report.get("source_locations", {}).items()
        }
        for subject_uuid in report.get("subjects", {}).copy():
            subject = report["subjects"][uuid()] = report["subjects"].pop(subject_uuid)
            for metric_uuid in subject.get("metrics", {}).copy():
                metric = subject["metrics"][uuid()] = subject["metrics"].pop(metric_uuid)
                for source_uuid in metric.get("sources").copy():
                    source = metric["sources"][uuid()] = metric["sources"].pop(source_uuid)
                    if location_uuid := source.get("source_location"):
                        source["source_location"] = new_location_uuids.get(location_uuid, location_uuid)


def add_source_locations(report) -> str:
    """Move the location parameters of the sources in the report to source locations at the report level.

    This migration is run on reports in the database at startup and on incoming reports with the old structure when
    they are imported. Skip reports that already have source locations to make the migration idempotent.
    """
    if "source_locations" in report:
        return ""
    locations: dict[str, dict[str, str]] = {}
    report["source_locations"] = locations
    location_uuids: dict[str, str] = {}
    for source in sources(report):
        if source["type"] in SOURCE_TYPES_WITHOUT_LOCATION:
            continue
        parameters = source.setdefault("parameters", {})
        location: dict[str, str] = {"location_name": source.get("name") or "", "source_type": source["type"]}
        for parameter_key in LOCATION_PARAMETERS:
            location[parameter_key] = parameters.pop(parameter_key, "") or ""
        # Reuse an existing source location if one with the same name, source type, and parameters exists:
        location_key = repr(sorted(location.items()))
        if location_key not in location_uuids:
            location_uuids[location_key] = uuid()
            locations[location_uuids[location_key]] = location
        source["source_location"] = location_uuids[location_key]
    return "add source locations"


def change_source_parameter(
    context: SourceContext,
    parameter_key: str,
    new_value: str | list[str],
) -> list[ItemId]:
    """Change the parameter of the source to the new value and return the ids of the changed items."""
    context.source["parameters"][parameter_key] = new_value
    return [context.report["report_uuid"], context.subject.uuid, context.metric.uuid, context.source.uuid]
