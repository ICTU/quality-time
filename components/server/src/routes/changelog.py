"""Changelog routes."""

from pymongo.database import Database
import bottle

from database import measurements, reports
from server_utilities.type import MetricId, ReportId, SourceId, SubjectId


def _get_changelog(database: Database, nr_changes: str, **uuids: str):
    """Return the recent most nr_changes changes from the changelog."""
    limit = int(nr_changes)
    changes = [
        dict(
            delta=item["delta"]["description"], email=item["delta"].get("email", ""),
            timestamp=item.get("timestamp") or item["start"])
        for item in measurements.changelog(database, limit, **uuids) + reports.changelog(database, limit, **uuids)]
    return dict(changelog=sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:limit])


@bottle.get("/api/v1/changelog/report/<report_uuid>/source/<source_uuid>/<nr_changes>")
def get_source_changelog_v1(report_uuid: ReportId, source_uuid: SourceId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the source changelog."""
    # pylint: disable=unused-argument
    return get_source_changelog(source_uuid, nr_changes, database)  # pragma: nocover


@bottle.get("/api/v2/changelog/source/<source_uuid>/<nr_changes>")
def get_source_changelog(source_uuid: SourceId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the source changelog."""
    return _get_changelog(database, nr_changes, source_uuid=source_uuid)


@bottle.get("/api/v1/changelog/report/<report_uuid>/metric/<metric_uuid>/<nr_changes>")
def get_metric_changelog_v1(report_uuid: ReportId, metric_uuid: MetricId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the metric changelog."""
    # pylint: disable=unused-argument
    return get_metric_changelog(metric_uuid, nr_changes, database)  # pragma: nocover


@bottle.get("/api/v2/changelog/metric/<metric_uuid>/<nr_changes>")
def get_metric_changelog(metric_uuid: MetricId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the metric changelog."""
    return _get_changelog(database, nr_changes, metric_uuid=metric_uuid)


@bottle.get("/api/v1/changelog/report/<report_uuid>/subject/<subject_uuid>/<nr_changes>")
def get_subject_changelog_v1(report_uuid: ReportId, subject_uuid: SubjectId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the subject changelog."""
    # pylint: disable=unused-argument
    return get_subject_changelog(subject_uuid, nr_changes, database)  # pragma: nocover


@bottle.get("/api/v2/changelog/subject/<subject_uuid>/<nr_changes>")
def get_subject_changelog(subject_uuid: SubjectId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the subject changelog."""
    return _get_changelog(database, nr_changes, subject_uuid=subject_uuid)


@bottle.get("/api/v1/changelog/report/<report_uuid>/<nr_changes>")
@bottle.get("/api/v2/changelog/report/<report_uuid>/<nr_changes>")
def get_report_changelog(report_uuid: ReportId, nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the report changelog."""
    return _get_changelog(database, nr_changes, report_uuid=report_uuid)


@bottle.get("/api/v1/changelog/<nr_changes>")
@bottle.get("/api/v2/changelog/<nr_changes>")
def get_changelog(nr_changes: str, database: Database):
    """Return the recent most nr_changes changes from the changelog."""
    return _get_changelog(database, nr_changes)
