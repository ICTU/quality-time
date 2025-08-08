"""Model transformations."""

import json
from typing import cast

from collections.abc import Iterator
from json.decoder import JSONDecodeError

from shared.utils.type import ItemId

from utils.functions import asymmetric_decrypt, asymmetric_encrypt, unique, uuid, DecryptionError
from utils.type import EditScope

from .iterators import sources as iter_sources
from .queries import is_password_parameter

CREDENTIALS_REPLACEMENT_TEXT = "this string replaces credentials"


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports. The data model must be passed so hiding also works when time traveling."""
    for source in iter_sources(*reports):
        for parameter_key in __password_parameter_keys(source, data_model):
            source["parameters"][parameter_key] = CREDENTIALS_REPLACEMENT_TEXT
    for report in reports:
        issue_tracker_parameters = report.get("issue_tracker", {}).get("parameters", {})
        for secret_attribute in ("password", "private_token"):
            if issue_tracker_parameters.get(secret_attribute):
                issue_tracker_parameters[secret_attribute] = CREDENTIALS_REPLACEMENT_TEXT


def encrypt_credentials(public_key: str, *reports: dict):
    """Encrypt all credentials in the reports."""
    encrypt_source_credentials(public_key, *reports)
    encrypt_issue_tracker_credentials(public_key, *reports)


def encrypt_source_credentials(public_key: str, *reports: dict):
    """Encrypt all source credentials in the reports."""
    for source in iter_sources(*reports):
        for parameter_key in __password_parameter_keys(source):
            password = source["parameters"][parameter_key]
            if isinstance(password, dict | list):
                password = json.dumps(password)
            source["parameters"][parameter_key] = asymmetric_encrypt(public_key, password)


def encrypt_issue_tracker_credentials(public_key: str, *reports: dict):
    """Encrypt all issue tracker credentials in the reports."""
    for report in reports:
        for secret_attribute in ("password", "private_token"):
            if secret_attribute in report.get("issue_tracker", {}).get("parameters", {}):
                password = report["issue_tracker"]["parameters"][secret_attribute]
                report["issue_tracker"]["parameters"][secret_attribute] = asymmetric_encrypt(public_key, password)


def decrypt_credentials(private_key: str, *reports: dict):
    """Decrypt all credentials in the reports."""
    decrypt_source_credentials(private_key, *reports)
    decrypt_issue_tracker_credentials(private_key, *reports)


def decrypt_source_credentials(private_key: str, *reports: dict):
    """Decrypt all source credentials in the reports."""
    for source in iter_sources(*reports):
        for parameter_key in __password_parameter_keys(source):
            credential = decrypt_credential(private_key, source["parameters"][parameter_key])
            source["parameters"][parameter_key] = credential


def decrypt_issue_tracker_credentials(private_key: str, *reports: dict):
    """Decrypt all issue tracker credentials in the reports."""
    for report in reports:
        for secret_attribute in ("password", "private_token"):
            if secret_attribute in report.get("issue_tracker", {}).get("parameters", {}):
                credential = decrypt_credential(private_key, report["issue_tracker"]["parameters"][secret_attribute])
                report["issue_tracker"]["parameters"][secret_attribute] = credential


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


def change_source_parameter(  # noqa: PLR0913
    reports,
    items,
    parameter_key: str,
    old_value,
    new_value,
    scope: EditScope,
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
    yield from (
        {subject.uuid: subject}.items()
        if scope
        in (
            "subject",
            "metric",
            "source",
        )
        else report.subjects_dict.items()
    )


def _metrics_to_change(subject, metric, scope: EditScope) -> Iterator:
    """Return the metrics to change, given the scope."""
    yield from {metric.uuid: metric}.items() if scope in ("metric", "source") else subject.metrics_dict.items()


def __sources_to_change(metric, source, scope: EditScope) -> Iterator:
    """Return the sources to change, given the scope."""
    yield from {source.uuid: source}.items() if scope == "source" else metric.sources_dict.items()


def __password_parameter_keys(source, data_model: dict | None = None) -> list[str]:
    """Return the password parameter keys of the source."""
    parameters = source.get("parameters", {}).items()
    return [key for key, value in parameters if value and is_password_parameter(source["type"], key, data_model)]
