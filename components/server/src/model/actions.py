"""Model operations."""

from typing import Dict, Literal, Tuple

from server_utilities.functions import uuid
from server_utilities.type import Position, ReportId


def copy_source(source, data_model, change_name: bool = True):
    """Return a copy of the source."""
    source_copy = source.copy()
    if change_name:
        name = source_copy.get("name") or data_model["sources"][source["type"]]["name"]
        source_copy["name"] = f"{name} (copy)"
    return source_copy


def copy_metric(metric, data_model, report_uuid: ReportId = None, change_name: bool = True):
    """Return a copy of the metric and its sources."""
    metric_copy = metric.copy()
    metric_copy["sources"] = dict(
        (uuid(), copy_source(source, data_model, change_name=False)) for source in metric["sources"].values())
    if change_name:
        name = metric_copy.get("name") or data_model["metrics"][metric["type"]]["name"]
        metric_copy["name"] = f"{name} (copy)"
    if report_uuid:
        metric_copy["report_uuid"] = report_uuid
    return metric_copy


def copy_subject(subject, data_model, report_uuid: ReportId = None, change_name: bool = True):
    """Return a copy of the subject, its metrics, and their sources."""
    subject_copy = subject.copy()
    subject_copy["metrics"] = dict(
        (uuid(), copy_metric(metric, data_model, report_uuid, change_name=False))
        for metric in subject["metrics"].values())
    if change_name:
        name = subject_copy.get("name") or data_model["subjects"][subject["type"]]["name"]
        subject_copy["name"] = f"{name} (copy)"
    return subject_copy


def copy_report(report, data_model, report_uuid: ReportId):
    """Return a copy of the report, its subjects, their metrics, and their sources."""
    report_copy = report.copy()
    report_copy["subjects"] = dict(
        (uuid(), copy_subject(subject, data_model, report_uuid, change_name=False))
        for subject in report["subjects"].values())
    report_copy["report_uuid"] = report_uuid
    report_copy["title"] = f"{report_copy['title']} (copy)"
    return report_copy


def move_item(data, new_position: Position, item_type: Literal["metric", "subject"]) -> Tuple[int, int]:
    """Change the item position."""
    container = data.report if item_type == "subject" else data.subject
    items = container[item_type + "s"]
    nr_items = len(items)
    item_to_move = getattr(data, item_type)
    item_to_move_id = getattr(data, f"{item_type}_uuid")
    old_index = list(items.keys()).index(item_to_move_id)
    new_index = dict(
        first=0, last=nr_items - 1, previous=max(0, old_index - 1), next=min(nr_items - 1, old_index + 1))[new_position]
    # Dicts are guaranteed to be (insertion) ordered starting in Python 3.7, but there's no API to change the order so
    # we construct a new dict in the right order and insert that in the report.
    reordered_items: Dict[str, Dict] = dict()
    del items[item_to_move_id]
    for item_id, item in items.items():
        if len(reordered_items) == new_index:
            reordered_items[item_to_move_id] = item_to_move
        reordered_items[item_id] = item
    if len(reordered_items) == new_index:
        reordered_items[item_to_move_id] = item_to_move
    container[item_type + "s"] = reordered_items
    return old_index, new_index
