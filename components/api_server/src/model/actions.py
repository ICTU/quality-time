"""Model operations."""

from collections.abc import MutableMapping
from typing import Any, cast

from shared.model.subject import Subject
from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.type import ItemId
from shared_data_model import DATA_MODEL

from model.report import Report
from utils.functions import uuid
from utils.type import Position


def copy_item(item, **kwargs):
    """Return a copy of the item."""
    item_copy = item.copy()
    for key, value in kwargs.items():
        item_copy[key] = value
    return item_copy


def copy_source(source, change_name: bool = True):
    """Return a copy of the source."""
    kwargs = {}
    if change_name:
        kwargs["name"] = f"{source.get('name') or DATA_MODEL.sources[source['type']].name} (copy)"
    return copy_item(source, **kwargs)


def copy_metric(metric, change_name: bool = True):
    """Return a copy of the metric and its sources."""
    kwargs: dict[str, Any] = {
        "sources": {uuid(): copy_source(source, change_name=False) for source in metric["sources"].values()},
    }
    if change_name:
        kwargs["name"] = f"{metric.get('name') or DATA_MODEL.metrics[metric['type']].name} (copy)"
    return copy_item(metric, **kwargs)


def copy_subject(subject, change_name: bool = True):
    """Return a copy of the subject, its metrics, and their sources."""
    kwargs: dict[str, Any] = {
        "metrics": {uuid(): copy_metric(metric, change_name=False) for metric in subject["metrics"].values()},
    }
    if change_name:
        kwargs["name"] = f"{subject.get('name') or DATA_MODEL.all_subjects[subject['type']].name} (copy)"
    return copy_item(subject, **kwargs)


def copy_report(report):
    """Return a copy of the report, its subjects, their metrics, and their sources."""
    return copy_item(
        report,
        report_uuid=uuid(),
        title=f"{report['title']} (copy)",
        subjects={uuid(): copy_subject(subject, change_name=False) for subject in report["subjects"].values()},
    )


def move_item(
    container: Report | Subject | Metric,
    item_to_move: Subject | Metric | Source,
    new_position: Position,
) -> tuple[int, int]:
    """Change the item position."""
    items_dict_type = MutableMapping[ItemId, Metric | Source | Subject]
    items_dict: items_dict_type
    if isinstance(container, Report):
        items_dict = cast(items_dict_type, container.subjects_dict)
    elif isinstance(container, Subject):
        items_dict = cast(items_dict_type, container.metrics_dict)
    else:
        items_dict = cast(items_dict_type, container.sources_dict)

    nr_items = len(items_dict)
    old_index = list(items_dict.keys()).index(item_to_move.uuid)
    new_index = {
        "first": 0,
        "last": nr_items - 1,
        "previous": max(0, old_index - 1),
        "next": min(nr_items - 1, old_index + 1),
    }[new_position]
    # Dicts are guaranteed to be (insertion) ordered starting in Python 3.7, but there's no API to change the order so
    # we construct a new dict in the right order and insert that in the report.
    reordered_items: dict[str, dict] = {}
    del items_dict[item_to_move.uuid]
    for item_id, item in items_dict.items():
        if len(reordered_items) == new_index:
            reordered_items[item_to_move.uuid] = item_to_move
        reordered_items[item_id] = item
    if len(reordered_items) == new_index:
        reordered_items[item_to_move.uuid] = item_to_move

    if isinstance(container, Report):
        container["subjects"] = reordered_items
    elif isinstance(container, Subject):
        container["metrics"] = reordered_items
    else:
        container["sources"] = reordered_items

    return old_index, new_index
