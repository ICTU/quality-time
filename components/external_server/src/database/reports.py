"""Reports collection."""

from typing import cast

import pymongo
from pymongo.database import Database

from shared.database import sessions
from shared.database.filters import DOES_EXIST, DOES_NOT_EXIST
from shared.model.report import Report
from shared.utils.functions import iso_timestamp
from shared.utils.type import MetricId, SubjectId

from utils.functions import unique
from utils.type import Change, ItemId


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.

    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid".
    """
    projection = {"delta": True, "timestamp": True}
    delta_filter: dict[str, dict | list] = {"delta": DOES_EXIST}
    changes: list[Change] = []
    if not uuids:
        changes.extend(
            database.reports_overviews.find(
                filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes * 2, projection=projection
            )
        )
    old_report_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    new_report_delta_filter = {"delta.uuids": {"$in": list(uuids.values())}}
    delta_filter["$or"] = [old_report_delta_filter, new_report_delta_filter]
    changes.extend(
        database.reports.find(
            filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes * 2, projection=projection
        )
    )
    changes = sorted(changes, reverse=True, key=lambda change: cast(str, change["timestamp"]))
    # Weed out potential duplicates, because when a user moves items between reports both reports get the same delta
    return list(unique(changes, _get_change_key))[:nr_changes]


def _get_change_key(change: Change) -> str:
    """Return a key for detecting equal changes."""
    description = cast(dict[str, str], change["delta"])["description"]
    changed_uuids = cast(dict[str, list[str]], change["delta"]).get("uuids", [])
    key = f"{change['timestamp']}:{','.join(sorted(changed_uuids))}:{description}"
    return key


def metrics_of_subject(database: Database, subject_uuid: SubjectId, max_iso_timestamp: str = "") -> list[MetricId]:
    """Return all metric uuid's for one subject, without the entities, except for the most recent one."""
    report_filter = {f"subjects.{subject_uuid}": DOES_EXIST}
    if max_iso_timestamp and max_iso_timestamp < iso_timestamp():
        report_filter["timestamp"] = {"$lt": max_iso_timestamp}
    else:
        report_filter["last"] = True
    projection: dict = {"_id": False, f"subjects.{subject_uuid}.metrics": True}
    report = database.reports.find_one(report_filter, projection=projection)
    return list(report["subjects"][subject_uuid]["metrics"].keys()) if report else []


def latest_report(database: Database, data_model, report_uuid: str):
    """Get latest report with this uuid."""
    report_dict = database.reports.find_one({"report_uuid": report_uuid, "last": True, "deleted": DOES_NOT_EXIST})
    return Report(data_model, report_dict) if report_dict else None


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def latest_reports(database: Database, data_model: dict, max_iso_timestamp: str = "") -> list[Report]:
    """Return the latest, undeleted, reports in the reports collection."""
    if max_iso_timestamp and max_iso_timestamp < iso_timestamp():
        report_filter = dict(timestamp={"$lt": max_iso_timestamp})
        report_uuids = database.reports.distinct("report_uuid", report_filter)
        report_dicts = []
        for report_uuid in report_uuids:
            report_filter["report_uuid"] = report_uuid
            report_dict = database.reports.find_one(report_filter, sort=TIMESTAMP_DESCENDING)
            if report_dict and "deleted" not in report_dict:
                report_dicts.append(report_dict)
    else:
        report_dicts = cast(list, database.reports.find({"last": True, "deleted": DOES_NOT_EXIST}))
    return [Report(data_model, report_dict) for report_dict in report_dicts]


def latest_report_for_uuids(all_reports: list[Report], *uuids: ItemId) -> list[Report]:
    """Return the report for given child entity uuids.

    The uuids can be of a report, subject, metric or source.
    The returned results will be in order of provided uuids.
    """
    reports = []
    for uuid in uuids:
        for report in all_reports:  # pragma: no cover-behave
            uuids_in_report = {report.uuid}.union(report.subject_uuids, report.metric_uuids, report.source_uuids)
            if uuid in uuids_in_report:
                reports.append(report)
                break
    return reports
