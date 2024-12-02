"""Model operations."""

from collections.abc import MutableMapping
from typing import Any, cast

from shared.model.subject import Subject
from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.type import ItemId

from model.report import Report
from utils.functions import uuid
from utils.type import Position


def copy_item[Item: Metric | Report | Source | Subject](item: Item, **kwargs) -> Item:
    """Return a copy of the item."""
    item_copy = cast(Item, item.copy())
    for key, value in kwargs.items():
        item_copy[key] = value
    return item_copy


def copy_source(source: Source) -> Source:
    """Return a copy of the source."""
    return copy_item(source)


def copy_metric(metric: Metric) -> Metric:
    """Return a copy of the metric and its sources."""
    kwargs: dict[str, Any] = {
        "sources": {uuid(): copy_source(source) for source in metric["sources"].values()},
    }
    return copy_item(metric, **kwargs)


def copy_subject(subject: Subject) -> Subject:
    """Return a copy of the subject, its metrics, and their sources."""
    kwargs: dict[str, Any] = {
        "metrics": {uuid(): copy_metric(metric) for metric in subject["metrics"].values()},
    }
    return copy_item(subject, **kwargs)


def copy_report(report: Report) -> Report:
    """Return a copy of the report, its subjects, their metrics, and their sources."""
    return copy_item(
        report,
        report_uuid=uuid(),
        subjects={uuid(): copy_subject(subject) for subject in report["subjects"].values()},
    )


type ItemsDictType = MutableMapping[ItemId, Metric | Source | Subject]


def move_item(
    container: Report | Subject | Metric,
    item_to_move: Subject | Metric | Source,
    new_position: Position,
) -> tuple[int, int]:
    """Change the item position."""
    items_dict: ItemsDictType
    if isinstance(container, Report):
        items_dict = cast(ItemsDictType, container.subjects_dict)
    elif isinstance(container, Subject):
        items_dict = cast(ItemsDictType, container.metrics_dict)
    else:
        items_dict = cast(ItemsDictType, container.sources_dict)

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
