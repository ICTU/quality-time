"""Model transformations."""

import json

from collections.abc import Iterator
from datetime import date
from json.decoder import JSONDecodeError
from typing import cast
from database.measurements import latest_measurements_by_metric_uuid, recent_measurements_by_metric_uuid
from server_utilities.functions import (
    DecryptionError,
    asymmetric_decrypt,
    asymmetric_encrypt,
    report_metrics_uuids,
    unique,
    uuid,
)
from server_utilities.type import Color, EditScope, ItemId, Status

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


def change_source_parameter(data, parameter_key: str, old_value, new_value, scope: EditScope) -> list[ItemId]:
    """Change the parameter of all sources of the specified type and the same old value to the new value.

    Return the ids of the changed reports, subjects, metrics, and sources.
    """
    changed_ids: list[ItemId] = []
    for source, uuids in _sources_to_change(data, scope):
        if source["type"] == data.source["type"] and (source["parameters"].get(parameter_key) or None) == (
            old_value or None
        ):
            source["parameters"][parameter_key] = new_value
            changed_ids.extend(uuids)
    return list(unique(changed_ids))


def _sources_to_change(data, scope: EditScope) -> Iterator:
    """Return the sources to change, given the scope."""
    for report in _reports_to_change(data, scope):
        for subject_uuid, subject in _subjects_to_change(data, report, scope):
            for metric_uuid, metric in _metrics_to_change(data, subject, scope):
                for source_uuid, source_to_change in __sources_to_change(data, metric, scope):
                    yield source_to_change, [report["report_uuid"], subject_uuid, metric_uuid, source_uuid]


def _reports_to_change(data, scope: EditScope) -> Iterator:
    """Return the reports to change, given the scope."""
    yield from data.reports if scope == "reports" else [data.report]


def _subjects_to_change(data, report, scope: EditScope) -> Iterator:
    """Return the subjects to change, given the scope."""
    yield from {data.subject_uuid: data.subject}.items() if scope in ("subject", "metric", "source") else report[
        "subjects"
    ].items()


def _metrics_to_change(data, subject, scope: EditScope) -> Iterator:
    """Return the metrics to change, given the scope."""
    yield from {data.metric_uuid: data.metric}.items() if scope in ("metric", "source") else subject["metrics"].items()


def __sources_to_change(data, metric, scope: EditScope) -> Iterator:
    """Return the sources to change, given the scope."""
    yield from {data.source_uuid: data.source}.items() if scope == "source" else metric["sources"].items()


def summarize_report(report, database, data_model, date_time) -> None:
    """Add a summary of the measurements to each subject."""
    report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=0)
    report["summary_by_subject"] = {}
    report["summary_by_tag"] = {}
    metric_uuids = report_metrics_uuids(report)
    recent_measurements = recent_measurements_by_metric_uuid(database, date_time, metric_uuids=metric_uuids)
    latest_measurements = latest_measurements_by_metric_uuid(database, metric_uuids)
    for subject_uuid, subject in report.get("subjects", {}).items():
        for metric_uuid in subject.get("metrics", {}):
            summarize_metric(data_model, recent_measurements, latest_measurements, report, subject_uuid, metric_uuid)


STATUS_COLOR_MAPPING = cast(
    dict[Status, Color],
    dict(target_met="green", debt_target_met="grey", near_target_met="yellow", target_not_met="red"),
)


# disable too-many-arguments for now, until refactor of measurements functions
def summarize_metric(
    data_model, recent_measurements, latest_measurements, report, subject_uuid, metric_uuid
):  # pylint: disable=too-many-arguments
    """Add a summary of the metric to the report."""
    metric = report["subjects"][subject_uuid]["metrics"][metric_uuid]
    latest_measurement = metric["latest_measurement"] = (
        latest_measurements[metric_uuid] if metric_uuid in latest_measurements else {}
    )
    metric["recent_measurements"] = recent_measurements.get(metric_uuid, [])
    scale = metric["scale"] = metric.get("scale") or data_model["metrics"][metric["type"]].get("default_scale", "count")
    metric["status"] = metric_status(metric, latest_measurement, scale)
    if status_start := latest_measurement.get(scale, {}).get("status_start"):
        metric["status_start"] = status_start
    metric["value"] = latest_measurement.get(scale, {}).get("value", latest_measurement.get("value"))
    if statuses := issue_statuses(metric, latest_measurement):
        metric["issue_status"] = statuses
    color = STATUS_COLOR_MAPPING.get(metric["status"], "white")
    report["summary"][color] += 1
    report["summary_by_subject"].setdefault(subject_uuid, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1
    for tag in metric.get("tags", []):
        report["summary_by_tag"].setdefault(tag, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1


def issue_statuses(metric, last_measurement) -> list[dict]:
    """Return the metric's issue  statuses."""
    last_issue_statuses = last_measurement.get("issue_status", [])
    return [status for status in last_issue_statuses if status["issue_id"] in metric.get("issue_ids", [])]


def metric_status(metric, last_measurement, scale) -> Status | None:
    """Determine the metric status."""
    if status := last_measurement.get(scale, {}).get("status", last_measurement.get("status")):
        return cast(Status, status)
    debt_end_date = metric.get("debt_end_date") or date.max.isoformat()
    return "debt_target_met" if metric.get("accept_debt") and date.today().isoformat() <= debt_end_date else None
