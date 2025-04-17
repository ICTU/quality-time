"""Model operations."""

from collections.abc import MutableMapping
from typing import cast

from shared.model.subject import Subject
from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.type import ItemId, MetricId, SourceId, SubjectId

from model.report import Report
from utils.functions import uuid
from utils.type import Position


def copy_item[Item: Metric | Report | Source | Subject](item: Item, **kwargs) -> Item:
    """Return a copy of the item."""
    item_copy = cast(Item, item.copy())
    for key, value in kwargs.items():
        item_copy[key] = value
    return item_copy


def copy_source(source_uuid: SourceId, source: Source) -> Source:
    """Return a copy of the source."""
    return copy_item(source, copied_from=source_uuid)


def copy_metric(metric_uuid: MetricId, metric: Metric) -> Metric:
    """Return a copy of the metric and its sources."""
    sources = {uuid(): copy_source(source_uuid, source) for source_uuid, source in metric["sources"].items()}
    return copy_item(metric, copied_from=metric_uuid, sources=sources)


def copy_subject(subject_uuid: SubjectId, subject: Subject) -> Subject:
    """Return a copy of the subject, its metrics, and their sources."""
    metrics = {uuid(): copy_metric(metric_uuid, metric) for metric_uuid, metric in subject["metrics"].items()}
    return copy_item(subject, copied_from=subject_uuid, metrics=metrics)


def copy_report(report: Report) -> Report:
    """Return a copy of the report, its subjects, their metrics, and their sources."""
    subjects = {uuid(): copy_subject(subject_uuid, subject) for subject_uuid, subject in report["subjects"].items()}
    return copy_item(report, report_uuid=uuid(), subjects=subjects, copied_from={"report": report.uuid})


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

def move_item_to_index(
    container: Report | Subject | Metric,
    item_to_move: Subject | Metric | Source,
    new_index: int,
) -> tuple[int, int]:
    items_dict: ItemsDictType
    if isinstance(container, Report):
        items_dict = cast(ItemsDictType, container.subjects_dict)
    elif isinstance(container, Subject):
        items_dict = cast(ItemsDictType, container.metrics_dict)
    else:
        items_dict = cast(ItemsDictType, container.sources_dict)

    item_keys = list(items_dict.keys())
    old_index = item_keys.index(item_to_move.uuid)

    # Clamp index
    new_index = max(0, min(new_index, len(item_keys) - 1))

    if old_index == new_index:
        return old_index, new_index  # no change

    # Remove the item key
    item_keys.pop(old_index)

    # Insert the item key at the new index
    item_keys.insert(new_index, item_to_move.uuid)

    # Rebuild the dict in the new order
    reordered_items = {key: items_dict.get(key, item_to_move) for key in item_keys}

    # Assign the new dict back to the container
    if isinstance(container, Report):
        container["subjects"] = reordered_items
    elif isinstance(container, Subject):
        container["metrics"] = reordered_items
    else:
        container["sources"] = reordered_items

    return old_index, new_index
