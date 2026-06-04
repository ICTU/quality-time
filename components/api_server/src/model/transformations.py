"""Model transformations."""

import json
from json.decoder import JSONDecodeError
from typing import cast, TYPE_CHECKING

from shared_data_model import DATA_MODEL

from utils.functions import asymmetric_decrypt, asymmetric_encrypt, unique, uuid, DecryptionError

from .iterators import credential_holders

if TYPE_CHECKING:
    from collections.abc import Iterator

    from shared.model.metric import Metric
    from shared.model.source import Source
    from shared.model.subject import Subject
    from shared.utils.type import ItemId, MetricId, ReportId, SourceId, SubjectId

    from model.report import Report
    from model.source import SourceContext
    from utils.type import EditScope


CREDENTIALS_REPLACEMENT_TEXT = "this string replaces credentials"


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
        for subject_uuid in report.get("subjects", {}).copy():
            subject = report["subjects"][uuid()] = report["subjects"].pop(subject_uuid)
            for metric_uuid in subject.get("metrics", {}).copy():
                metric = subject["metrics"][uuid()] = subject["metrics"].pop(metric_uuid)
                for source_uuid in metric.get("sources").copy():
                    metric["sources"][uuid()] = metric["sources"].pop(source_uuid)


def change_source_parameter(
    context: SourceContext,
    parameter_key: str,
    old_value: str | list[str],
    new_value: str | list[str],
    scope: EditScope,
) -> tuple[list[ItemId], set[ItemId]]:
    """Change the parameter of all sources of the specified type and the same old value to the new value.

    Return the ids of the changed reports, subjects, metrics, and sources.
    """
    changed_ids: list[ItemId] = []
    changed_source_uuids: set[ItemId] = set()
    for source_to_change, uuids in _all_sources_to_change(context, scope, parameter_key, old_value):
        source_to_change["parameters"][parameter_key] = new_value
        changed_ids.extend(uuids)
        changed_source_uuids.add(uuids[-1])
    return list(unique(changed_ids)), changed_source_uuids


def _all_sources_to_change(
    context: SourceContext,
    scope: EditScope,
    parameter_key: str,
    old_value: str | list[str],
) -> Iterator[tuple[Source, tuple[ReportId, SubjectId, MetricId, SourceId]]]:
    """Return the sources to change, given the scope."""
    for subject_uuid, subject in _subjects_to_change(context.report, context.subject, scope):
        for metric_uuid, metric in _metrics_to_change(subject, context.metric, scope):
            for source_uuid, source in _sources_to_change(metric, context.source, scope, parameter_key, old_value):
                yield source, (context.report["report_uuid"], subject_uuid, metric_uuid, source_uuid)


def _subjects_to_change(report: Report, subject: Subject, scope: EditScope) -> Iterator[tuple[SubjectId, Subject]]:
    """Return the subjects to change, given the scope."""
    yield from {subject.uuid: subject}.items() if scope == "source" else report.subjects_dict.items()


def _metrics_to_change(subject: Subject, metric: Metric, scope: EditScope) -> Iterator[tuple[MetricId, Metric]]:
    """Return the metrics to change, given the scope."""
    yield from {metric.uuid: metric}.items() if scope == "source" else subject.metrics_dict.items()


def _sources_to_change(
    metric: Metric,
    source: Source,
    scope: EditScope,
    parameter_key: str,
    old_value: str | list[str],
) -> Iterator[tuple[SourceId, Source]]:
    """Return the sources to change, given the scope."""
    if metric["type"] in DATA_MODEL.sources[source["type"]].parameters[parameter_key].metrics:
        if scope == "source":
            sources_to_change = {source.uuid: source}
        else:
            sources_to_change = {
                source_uuid: source_to_change
                for source_uuid, source_to_change in metric.sources_dict.items()
                if source.type == source_to_change.type
                and (source_to_change["parameters"].get(parameter_key) or None) == (old_value or None)
            }
    else:
        sources_to_change = {}  # pragma: no feature-test-cover
    yield from sources_to_change.items()
