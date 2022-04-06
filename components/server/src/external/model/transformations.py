"""Model transformations."""

import json

from collections.abc import Iterator
from json.decoder import JSONDecodeError

from ..utils.functions import asymmetric_decrypt, asymmetric_encrypt, unique, uuid, DecryptionError
from ..utils.type import EditScope, ItemId

from .iterators import sources as iter_sources
from .queries import is_password_parameter


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports."""
    hidden = "this string replaces credentials"
    for source in iter_sources(*reports):
        for parameter_key, parameter_value in source.get("parameters", {}).items():
            if parameter_value and is_password_parameter(data_model, source["type"], parameter_key):
                source["parameters"][parameter_key] = hidden
    for report in reports:
        for secret_attribute in ("password", "private_token"):
            if secret_attribute in report.get("issue_tracker", {}).get("parameters", {}):
                report["issue_tracker"]["parameters"][secret_attribute] = hidden


def encrypt_credentials(data_model, public_key: str, *reports: dict):
    """Encrypt all credentials in the reports."""
    encrypt_source_credentials(data_model, public_key, *reports)
    encrypt_issue_tracker_credentials(public_key, *reports)


def encrypt_source_credentials(data_model, public_key: str, *reports: dict):
    """Encrypt all source credentials in the reports."""
    for source in iter_sources(*reports):
        for parameter_key, parameter_value in source.get("parameters", {}).items():
            if parameter_value and is_password_parameter(data_model, source["type"], parameter_key):
                password = source["parameters"][parameter_key]
                if isinstance(password, (dict, list)):
                    password = json.dumps(password)
                source["parameters"][parameter_key] = asymmetric_encrypt(public_key, password)


def encrypt_issue_tracker_credentials(public_key: str, *reports: dict):
    """Encrypt all issue tracker credentials in the reports."""
    for report in reports:
        for secret_attribute in ("password", "private_token"):
            if secret_attribute in report.get("issue_tracker", {}).get("parameters", {}):
                password = report["issue_tracker"]["parameters"][secret_attribute]
                report["issue_tracker"]["parameters"][secret_attribute] = asymmetric_encrypt(public_key, password)


def decrypt_credentials(data_model, private_key: str, *reports: dict):
    """Decrypt all credentials in the reports."""
    decrypt_source_credentials(data_model, private_key, *reports)
    decrypt_issue_tracker_credentials(private_key, *reports)


def decrypt_source_credentials(data_model, private_key: str, *reports: dict):
    """Decrypt all source credentials in the reports."""
    for source in iter_sources(*reports):
        for parameter_key, parameter_value in source.get("parameters", {}).items():
            if parameter_value and is_password_parameter(data_model, source["type"], parameter_key):
                credential = decrypt_credential(private_key, source["parameters"][parameter_key])
                source["parameters"][parameter_key] = credential


def decrypt_issue_tracker_credentials(private_key: str, *reports: dict):
    """Decrypt all issue tracker credentials in the reports."""
    for report in reports:
        for secret_attribute in ("password", "private_token"):
            if secret_attribute in report.get("issue_tracker", {}).get("parameters", {}):
                credential = decrypt_credential(private_key, report["issue_tracker"]["parameters"][secret_attribute])
                report["issue_tracker"]["parameters"][secret_attribute] = credential


def decrypt_credential(private_key: str, credential: str | tuple[str, str]) -> str:
    """Decrypt the credential if it's encrypted, otherwise return it unchanged."""
    if isinstance(credential, str):
        return credential
    try:
        decrypted_credential = asymmetric_decrypt(private_key, credential)
    except ValueError as error:
        raise DecryptionError from error
    try:
        decrypted_credential = json.loads(decrypted_credential)
    except JSONDecodeError:
        pass
    return decrypted_credential


def replace_report_uuids(*reports) -> None:
    """Change all uuids in this report."""
    for report in reports:
        report["report_uuid"] = uuid()
        for subject_uuid, subject in list(report.get("subjects", {}).items()):
            report["subjects"][uuid()] = report["subjects"].pop(subject_uuid)
            for metric_uuid, metric in list(subject.get("metrics", {}).items()):
                subject["metrics"][uuid()] = subject["metrics"].pop(metric_uuid)
                for source_uuid in list(metric.get("sources").keys()):
                    metric["sources"][uuid()] = metric["sources"].pop(source_uuid)


def change_source_parameter(  # pylint: disable=too-many-arguments
    reports, items, parameter_key: str, old_value, new_value, scope: EditScope
) -> tuple[list[ItemId], set[ItemId]]:
    """Change the parameter of all sources of the specified type and the same old value to the new value.

    Return the ids of the changed reports, subjects, metrics, and sources.
    """
    changed_ids: list[ItemId] = []
    changed_source_uuids: set[ItemId] = set()
    for source, uuids in _sources_to_change(reports, items, scope):
        if source["type"] == items[0].type and (source["parameters"].get(parameter_key) or None) == (old_value or None):
            source["parameters"][parameter_key] = new_value
            changed_ids.extend(uuids)
            changed_source_uuids.add(uuids[-1])
    return list(unique(changed_ids)), changed_source_uuids


def _sources_to_change(reports, items, scope: EditScope) -> Iterator:
    """Return the sources to change, given the scope."""
    for report in _reports_to_change(reports, items[-1], scope):
        for subject_uuid, subject in _subjects_to_change(report, items[2], scope):
            for metric_uuid, metric in _metrics_to_change(subject, items[1], scope):
                for source_uuid, source_to_change in __sources_to_change(metric, items[0], scope):
                    yield source_to_change, [report["report_uuid"], subject_uuid, metric_uuid, source_uuid]


def _reports_to_change(reports, report, scope: EditScope) -> Iterator:
    """Return the reports to change, given the scope."""
    yield from reports if scope == "reports" else [report]


def _subjects_to_change(report, subject, scope: EditScope) -> Iterator:
    """Return the subjects to change, given the scope."""
    yield from {subject.uuid: subject}.items() if scope in (
        "subject",
        "metric",
        "source",
    ) else report.subjects_dict.items()


def _metrics_to_change(subject, metric, scope: EditScope) -> Iterator:
    """Return the metrics to change, given the scope."""
    yield from {metric.uuid: metric}.items() if scope in ("metric", "source") else subject.metrics_dict.items()


def __sources_to_change(metric, source, scope: EditScope) -> Iterator:
    """Return the sources to change, given the scope."""
    yield from {source.uuid: source}.items() if scope == "source" else metric.sources_dict.items()
