"""Reports collection."""

from collections.abc import Sequence
from typing import Any, cast

import pymongo
from pymongo.database import Database

from shared.database.filters import DOES_EXIST, DOES_NOT_EXIST
from shared.database.reports import get_reports
from shared.utils.functions import iso_timestamp
from shared.utils.type import ItemId, ReportId
from shared_data_model import DATA_MODEL

from model.report import Report
from utils.functions import unique
from utils.type import Change

from . import sessions


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
                filter=delta_filter,
                sort=TIMESTAMP_DESCENDING,
                limit=nr_changes * 2,
                projection=projection,
            ),
        )
    old_report_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    new_report_delta_filter = {"delta.uuids": {"$in": list(uuids.values())}}
    delta_filter["$or"] = [old_report_delta_filter, new_report_delta_filter]
    changes.extend(
        database.reports.find(
            filter=delta_filter,
            sort=TIMESTAMP_DESCENDING,
            limit=nr_changes * 2,
            projection=projection,
        ),
    )
    changes = sorted(changes, reverse=True, key=lambda change: cast(str, change["timestamp"]))
    # Weed out potential duplicates, because when a user moves items between reports both reports get the same delta
    return list(unique(changes, _get_change_key))[:nr_changes]


def _get_change_key(change: Change) -> str:
    """Return a key for detecting equal changes."""
    description = cast(dict[str, str], change["delta"])["description"]
    changed_uuids = cast(dict[str, list[str]], change["delta"]).get("uuids", [])
    return f"{change['timestamp']}:{','.join(sorted(changed_uuids))}:{description}"


def latest_report(database: Database, report_uuid: str) -> Report | None:
    """Get latest report with this uuid."""
    report_dict = database.reports.find_one({"report_uuid": report_uuid, "last": True, "deleted": DOES_NOT_EXIST})
    return Report(DATA_MODEL.model_dump(), report_dict) if report_dict else None


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def latest_reports(database: Database) -> list[Report]:
    """Return the latest, undeleted, reports in the reports collection."""
    return cast(list[Report], get_reports(database, Report))


def latest_reports_before_timestamp(database: Database, data_model: dict, max_iso_timestamp: str) -> list[Report]:
    """Return the latest, undeleted, reports in the reports collection before the max timestamp."""
    report_filter = {"timestamp": {"$lt": max_iso_timestamp}} if max_iso_timestamp else {}
    report_uuids = database.reports.distinct("report_uuid", report_filter)
    report_dicts = []
    for report_uuid in report_uuids:
        report_filter["report_uuid"] = report_uuid
        report_dict = database.reports.find_one(report_filter, sort=TIMESTAMP_DESCENDING)
        if report_dict and "deleted" not in report_dict:
            report_dicts.append(report_dict)
    return [Report(data_model, report_dict) for report_dict in report_dicts]


def latest_report_for_uuids(all_reports: list[Report], *uuids: ItemId) -> list[Report]:
    """Return the report for given child entity uuids.

    The uuids can be of a report, subject, metric or source.
    The returned results will be in order of provided uuids.
    """
    reports = []
    for uuid in uuids:
        for report in all_reports:  # pragma: no feature-test-cover
            uuids_in_report = {report.uuid}.union(report.subject_uuids, report.metric_uuids, report.source_uuids)
            if uuid in uuids_in_report:
                reports.append(report)
                break
    return reports


def report_exists(database: Database, report_uuid: ReportId) -> bool:
    """Return whether a report with the specified report uuid exists."""
    return report_uuid in database.reports.distinct("report_uuid")


def insert_new_reports_overview(database: Database, delta_description: str, reports_overview: dict) -> dict[str, Any]:
    """Insert a new reports overview in the reports overview collection."""
    prepare_documents_for_insertion(database, delta_description, [reports_overview])
    database.reports_overviews.insert_one(reports_overview)
    return {"ok": True}


def latest_reports_overview(database: Database, max_iso_timestamp: str = "") -> dict:
    """Return the latest reports overview."""
    timestamp_filter = {"timestamp": {"$lt": max_iso_timestamp}} if max_iso_timestamp else None
    overview = database.reports_overviews.find_one(timestamp_filter, sort=TIMESTAMP_DESCENDING)
    if overview:  # pragma: no feature-test-cover
        overview["_id"] = str(overview["_id"])
    return overview or {}


def insert_new_report(
    database: Database,
    delta_description: str,
    uuids: list[ItemId],
    *reports: dict,
) -> dict[str, Any]:
    """Insert one or more new reports in the reports collection."""
    prepare_documents_for_insertion(database, delta_description, reports, uuids, last=True)
    report_uuids = [report["report_uuid"] for report in reports]
    database.reports.update_many({"report_uuid": {"$in": report_uuids}, "last": DOES_EXIST}, {"$unset": {"last": ""}})
    if len(reports) > 1:
        database.reports.insert_many(reports, ordered=False)
    else:
        database.reports.insert_one(reports[0])
    return {"ok": True}


def prepare_documents_for_insertion(
    database: Database,
    delta_description: str,
    documents: Sequence[dict],
    uuids: list[ItemId] | None = None,
    **extra_attributes,
) -> None:
    """Prepare the documents for insertion in the database by removing any ids and setting the extra attributes."""
    now = iso_timestamp()
    user = sessions.find_user(database)
    username = user.name() or "An operator"
    # Don't use str.format because there may be curly braces in the delta description, e.g. due to regular expressions:
    description = delta_description.replace("{user}", username, 1)
    for document in documents:
        if "_id" in document:
            del document["_id"]
        document["timestamp"] = now
        document["delta"] = {"description": description, "email": user.email, "uuids": sorted(set(uuids or []))}
        for key, value in extra_attributes.items():
            document[key] = value
