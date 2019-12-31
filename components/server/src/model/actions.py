"""Model operations."""

from typing import Dict, Literal, Tuple

from server_utilities.functions import uuid
from server_utilities.type import Position


def copy_item(item, **kwargs):
    """Return a copy of the item."""
    item_copy = item.copy()
    for key, value in kwargs.items():
        item_copy[key] = value
    return item_copy


def copy_source(source, data_model, change_name: bool = True):
    """Return a copy of the source."""
    kwargs = {}
    if change_name:
        kwargs["name"] = f"{source.get('name') or data_model['sources'][source['type']]['name']} (copy)"
    return copy_item(source, **kwargs)


def copy_metric(metric, data_model, change_name: bool = True, **kwargs):
    """Return a copy of the metric and its sources."""
    kwargs["sources"] = dict(
        (uuid(), copy_source(source, data_model, change_name=False)) for source in metric["sources"].values())
    if change_name:
        kwargs["name"] = f"{metric.get('name') or data_model['metrics'][metric['type']]['name']} (copy)"
    return copy_item(metric, **kwargs)


def copy_subject(subject, data_model, change_name: bool = True, **kwargs):
    """Return a copy of the subject, its metrics, and their sources."""
    kwargs["metrics"] = dict(
        (uuid(), copy_metric(metric, data_model, change_name=False, **kwargs))
        for metric in subject["metrics"].values())
    if change_name:
        kwargs["name"] = f"{subject.get('name') or data_model['subjects'][subject['type']]['name']} (copy)"
    kwargs.pop("report_uuid", None)  # Subjects don't have a report uuid, but metrics do.
    return copy_item(subject, **kwargs)


def copy_report(report, data_model):
    """Return a copy of the report, its subjects, their metrics, and their sources."""
    report_uuid = uuid()
    return copy_item(
        report, report_uuid=report_uuid, title=f"{report['title']} (copy)",
        subjects=dict(
            (uuid(), copy_subject(subject, data_model, change_name=False, report_uuid=report_uuid))
            for subject in report["subjects"].values()))


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
