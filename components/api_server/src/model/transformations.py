"""Model transformations."""

import json
from json.decoder import JSONDecodeError
from typing import cast, TYPE_CHECKING

from shared_data_model import DATA_MODEL

from utils.functions import asymmetric_decrypt, asymmetric_encrypt, unique, uuid, DecryptionError

from .iterators import sources as iter_sources
from .queries import is_password_parameter

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from shared.model.metric import Metric
    from shared.model.source import Source
    from shared.model.subject import Subject
    from shared.utils.type import ItemId, MetricId, ReportId, SourceId, SubjectId

    from model.report import Report
    from utils.type import EditScope, SourceContext


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
    reports: Sequence[Report],
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
    for source_to_change, uuids in _all_sources_to_change(reports, context, scope, parameter_key, old_value):
        source_to_change["parameters"][parameter_key] = new_value
        changed_ids.extend(uuids)
        changed_source_uuids.add(uuids[-1])
    return list(unique(changed_ids)), changed_source_uuids


def _all_sources_to_change(
    reports: Sequence[Report],
    context: SourceContext,
    scope: EditScope,
    parameter_key: str,
    old_value: str | list[str],
) -> Iterator[tuple[Source, tuple[ReportId, SubjectId, MetricId, SourceId]]]:
    """Return the sources to change, given the scope."""
    for report_uuid, report in _reports_to_change(reports, context.report, scope):
        for subject_uuid, subject in _subjects_to_change(report, context.subject, scope):
            for metric_uuid, metric in _metrics_to_change(subject, context.metric, scope):
                for source_uuid, source in _sources_to_change(metric, context.source, scope, parameter_key, old_value):
                    yield source, (report_uuid, subject_uuid, metric_uuid, source_uuid)


def _reports_to_change(
    reports: Sequence[Report], report: Report, scope: EditScope
) -> Iterator[tuple[ReportId, Report]]:
    """Return the reports to change, given the scope."""
    reports_to_change = reports if scope == "reports" else [report]
    yield from {report["report_uuid"]: report for report in reports_to_change}.items()


def _subjects_to_change(report: Report, subject: Subject, scope: EditScope) -> Iterator[tuple[SubjectId, Subject]]:
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


def _metrics_to_change(subject: Subject, metric: Metric, scope: EditScope) -> Iterator[tuple[MetricId, Metric]]:
    """Return the metrics to change, given the scope."""
    yield from {metric.uuid: metric}.items() if scope in ("metric", "source") else subject.metrics_dict.items()


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
        sources_to_change = {}
    yield from sources_to_change.items()


def __password_parameter_keys(source: Source, data_model: dict | None = None) -> list[str]:
    """Return the password parameter keys of the source."""
    parameters = source.get("parameters", {}).items()
    return [key for key, value in parameters if value and is_password_parameter(source["type"], key, data_model)]
