"""Changelog routes."""

from typing import TypedDict, TYPE_CHECKING

import bottle

from database import measurements, reports

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.utils.type import MetricId, ReportId, SourceId, SubjectId


class ChangelogEntry(TypedDict):
    """Changelog entry."""

    delta: str
    email: str
    timestamp: str


class ChangelogJSON(TypedDict):
    """Changelog JSON."""

    changelog: list[ChangelogEntry]


def _get_changelog(database: Database, nr_changes: int, **uuids: str) -> ChangelogJSON:
    """Return the recent most nr_changes changes from the changelog."""
    changes = [
        ChangelogEntry(
            delta=str(item["delta"]["description"]),
            email=str(item["delta"].get("email", "")),
            timestamp=str(item.get("timestamp") or item["start"]),
        )
        for item in list(measurements.changelog(database, nr_changes, **uuids))
        + list(reports.changelog(database, nr_changes, **uuids))
    ]
    return {"changelog": sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:nr_changes]}


@bottle.get("/api/internal/changelog/source/<source_uuid>/<nr_changes:int>", authentication_required=False)
def get_source_changelog(source_uuid: SourceId, nr_changes: int, database: Database) -> ChangelogJSON:
    """Return the recent most nr_changes changes from the source changelog."""
    return _get_changelog(database, nr_changes, source_uuid=source_uuid)


@bottle.get("/api/internal/changelog/metric/<metric_uuid>/<nr_changes:int>", authentication_required=False)
def get_metric_changelog(metric_uuid: MetricId, nr_changes: int, database: Database) -> ChangelogJSON:
    """Return the recent most nr_changes changes from the metric changelog."""
    return _get_changelog(database, nr_changes, metric_uuid=metric_uuid)


@bottle.get("/api/internal/changelog/subject/<subject_uuid>/<nr_changes:int>", authentication_required=False)
def get_subject_changelog(subject_uuid: SubjectId, nr_changes: int, database: Database) -> ChangelogJSON:
    """Return the recent most nr_changes changes from the subject changelog."""
    return _get_changelog(database, nr_changes, subject_uuid=subject_uuid)


@bottle.get("/api/internal/changelog/report/<report_uuid>/<nr_changes:int>", authentication_required=False)
def get_report_changelog(report_uuid: ReportId, nr_changes: int, database: Database) -> ChangelogJSON:
    """Return the recent most nr_changes changes from the report changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid)


@bottle.get("/api/internal/changelog/<nr_changes:int>", authentication_required=False)
def get_changelog(nr_changes: int, database: Database) -> ChangelogJSON:
    """Return the recent most nr_changes changes from the changelog."""
    return _get_changelog(database, nr_changes)
