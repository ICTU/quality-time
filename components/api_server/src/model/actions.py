"""Model operations."""

from collections.abc import MutableMapping
from typing import cast, TYPE_CHECKING

from shared.model.iterators import sources
from shared.model.subject import Subject
from shared.model.metric import Metric
from shared.model.source import Source
from shared.utils.type import ItemId, MetricId, SourceId, SubjectId

from model.report import Report
from utils.functions import uuid

if TYPE_CHECKING:
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
    """Return a copy of the report, its source locations, its subjects, their metrics, and their sources."""
    subjects = {uuid(): copy_subject(subject_uuid, subject) for subject_uuid, subject in report["subjects"].items()}
    new_location_uuids = {location_uuid: uuid() for location_uuid in report.get("source_locations", {})}
    source_locations = {
        new_location_uuids[location_uuid]: dict(location)
        for location_uuid, location in report.get("source_locations", {}).items()
    }
    for subject in subjects.values():
        for metric in subject["metrics"].values():
            for source in metric["sources"].values():
                if location_uuid := source.get("source_location"):
                    source["source_location"] = new_location_uuids.get(location_uuid, location_uuid)
    return copy_item(
        report,
        report_uuid=uuid(),
        subjects=subjects,
        source_locations=source_locations,
        copied_from={"report": report.uuid},
    )


def import_referenced_source_locations(  # pragma: no feature-test-cover
    target_report: Report,
    source_report: Report,
) -> list[ItemId]:
    """Copy source locations from the source report to the target report when sources refer to them.

    When sources are copied or moved between reports, the sources may refer to source locations that only exist in
    the source report. Copy these source locations to the target report, reusing equal source locations that already
    exist in the target report. Return the uuids of the source locations added to the target report.
    """
    if target_report.uuid == source_report.uuid:
        return []
    target_locations = target_report.setdefault("source_locations", {})
    new_location_uuids: dict[ItemId, ItemId] = {}
    added_location_uuids: list[ItemId] = []
    for source in sources(target_report):
        location_uuid = source.get("source_location")
        if not location_uuid or location_uuid in target_locations:
            continue
        if location_uuid in new_location_uuids:
            source["source_location"] = new_location_uuids[location_uuid]
            continue
        location = source_report.get("source_locations", {}).get(location_uuid)
        if location is None:
            source["source_location"] = ""
            continue
        for target_location_uuid, target_location in target_locations.items():
            if target_location == location:
                new_location_uuids[location_uuid] = target_location_uuid
                break
        else:
            new_location_uuid = uuid()
            target_locations[new_location_uuid] = dict(location)
            new_location_uuids[location_uuid] = new_location_uuid
            added_location_uuids.append(new_location_uuid)
        source["source_location"] = new_location_uuids[location_uuid]
    return added_location_uuids


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

    reordered_items = _reorder_items_dict(items_dict, item_to_move, new_index)

    if isinstance(container, Report):
        container["subjects"] = reordered_items
    elif isinstance(container, Subject):
        container["metrics"] = reordered_items
    else:
        container["sources"] = reordered_items

    return old_index, new_index


def move_metric_to_index(
    container: Subject,
    item_to_move: Metric,
    new_index: int,
) -> tuple[int, int]:
    """Change a metric position to a specific index within the subject."""
    items_dict: ItemsDictType
    items_dict = cast(ItemsDictType, container.metrics_dict)

    item_keys = list(items_dict.keys())
    # Clamp new index
    new_index = max(0, min(new_index, len(item_keys) - 1))
    old_index = item_keys.index(item_to_move.uuid)

    if old_index == new_index:
        return old_index, new_index

    # Create a new reordered dict
    reordered_items = _reorder_items_dict(items_dict, item_to_move, new_index)

    # Assign the new dict back to the container
    container["metrics"] = reordered_items

    return old_index, new_index


def _reorder_items_dict(
    items_dict: ItemsDictType,
    item_to_move: Subject | Metric | Source,
    new_index: int,
) -> dict[str, dict]:
    """Return a reordered dict with item_to_move at new_index."""
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
    return reordered_items
