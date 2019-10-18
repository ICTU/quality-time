"""Changelog routes."""

from pymongo.database import Database
import bottle

from database import measurements, reports
from utilities.type import MetricId, ReportId, SourceId, SubjectId


def get_changelog(database: Database, nr_changes: str, report_uuid: ReportId, **uuids: str):
    """Return the recent most nr_changes changes from the changelog."""
    limit = int(nr_changes)
    changes = [dict(delta=change["delta"], timestamp=change["start"])
               for change in measurements.changelog(database, report_uuid, limit)]
    changes.extend(
        [dict(delta=change["delta"]["description"], timestamp=change["timestamp"]) for change in
         reports.changelog(database, limit, **uuids)])
    return dict(changelog=sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:limit])


@bottle.get("/changelog/report/<report_uuid>/source/<source_uuid>/<nr_changes>")
def get_source_changelog(report_uuid: ReportId, source_uuid: SourceId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the source changelog."""
    return get_changelog(database, nr_changes, report_uuid, source_uuid=source_uuid)


@bottle.get("/changelog/report/<report_uuid>/metric/<metric_uuid>/<nr_changes>")
def get_metric_changelog(report_uuid: ReportId, metric_uuid: MetricId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the metric changelog."""
    return get_changelog(database, nr_changes, report_uuid, metric_uuid=metric_uuid)


@bottle.get("/changelog/report/<report_uuid>/subject/<subject_uuid>/<nr_changes>")
def get_subject_changelog(report_uuid: ReportId, subject_uuid: SubjectId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the subject changelog."""
    return get_changelog(database, nr_changes, report_uuid, subject_uuid=subject_uuid)


@bottle.get("/changelog/report/<report_uuid>/<nr_changes>")
def get_report_changelog(report_uuid: ReportId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the report changelog."""
    return get_changelog(database, nr_changes, report_uuid)
