"""Model transformations."""

from datetime import date
from typing import cast, Dict, Iterator, List, Optional

from server_utilities.functions import unique
from server_utilities.type import Color, EditScope, ItemId, Status
from .iterators import sources as iter_sources
from .queries import is_password_parameter


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports."""
    for source in iter_sources(reports):
        for parameter_key, parameter_value in source.get("parameters", {}).items():
            if parameter_value and is_password_parameter(data_model, source["type"], parameter_key):
                source["parameters"][parameter_key] = "this string replaces credentials"


def change_source_parameter(data, parameter_key: str, old_value, new_value, scope: EditScope) -> List[ItemId]:
    """Change the parameter with the specified key of all sources of the specified type and with the same old value to
    the new value. Return the ids of the changed reports, subjects, metrics, and sources."""
    changed_ids: List[ItemId] = []
    for source, uuids in _sources_to_change(data, scope):
        if source["type"] == data.source["type"] and \
                (source["parameters"].get(parameter_key) or None) == (old_value or None):
            source["parameters"][parameter_key] = new_value
            changed_ids.extend(uuids)
    return list(unique(changed_ids))


def _sources_to_change(data, scope: EditScope) -> Iterator:
    """Return the sources to change, given the scope."""
    reports = data.reports if scope == "reports" else [data.report]
    for report in reports:
        subjects = {data.subject_uuid: data.subject} if scope in ("subject", "metric", "source") else report["subjects"]
        for subject_uuid, subject in subjects.items():
            metrics = {data.metric_uuid: data.metric} if scope in ("metric", "source") else subject["metrics"]
            for metric_uuid, metric in metrics.items():
                sources = {data.source_uuid: data.source} if scope == "source" else metric["sources"]
                for source_uuid, source_to_change in sources.items():
                    yield source_to_change, [report["report_uuid"], subject_uuid, metric_uuid, source_uuid]


def summarize_report(report, recent_measurements, data_model) -> None:
    """Add a summary of the measurements to each subject."""
    status_color_mapping: Dict[Status, Color] = cast(Dict[Status, Color], dict(
        target_met="green", debt_target_met="grey", near_target_met="yellow", target_not_met="red"))
    report["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=0)
    report["summary_by_subject"] = {}
    report["summary_by_tag"] = {}
    for subject_uuid, subject in report.get("subjects", {}).items():
        for metric_uuid, metric in subject.get("metrics", {}).items():
            recent = metric["recent_measurements"] = recent_measurements.get(metric_uuid, [])
            scale = metric.get("scale") or data_model["metrics"][metric["type"]].get("default_scale", "count")
            metric["scale"] = scale
            last_measurement = recent[-1] if recent else {}
            metric["status"] = metric_status(metric, last_measurement, scale)
            metric["value"] = last_measurement.get(scale, {}).get("value", last_measurement.get("value"))
            color = status_color_mapping.get(metric["status"], "white")
            report["summary"][color] += 1
            report["summary_by_subject"].setdefault(
                subject_uuid, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1
            for tag in metric.get("tags", []):
                report["summary_by_tag"].setdefault(tag, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1


def metric_status(metric, last_measurement, scale) -> Optional[Status]:
    """Determine the metric status."""
    if status := last_measurement.get(scale, {}).get("status", last_measurement.get("status")):
        return cast(Status, status)
    debt_end_date = metric.get("debt_end_date") or date.max.isoformat()
    return "debt_target_met" if metric.get("accept_debt") and date.today().isoformat() <= debt_end_date else None
