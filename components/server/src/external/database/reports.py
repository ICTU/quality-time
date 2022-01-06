"""Reports collection."""

from typing import cast, Any

import pymongo
from pymongo.database import Database

from shared.database.filters import DOES_EXIST, DOES_NOT_EXIST
from shared.model.report import Report
from shared.utils.functions import iso_timestamp
from shared.utils.type import MetricId, ReportId, SubjectId

from ..database import sessions
from ..utils.functions import unique
from ..utils.type import Change


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


def metrics_of_subject(database: Database, subject_uuid: SubjectId) -> list[MetricId]:
    """Return all metric uuid's for one subject, without the entities, except for the most recent one."""
    report_filter: dict = {f"subjects.{subject_uuid}": DOES_EXIST, "last": True}
    projection: dict = {"_id": False, f"subjects.{subject_uuid}.metrics": True}
    report = database.reports.find_one(report_filter, projection=projection)
    return list(report["subjects"][subject_uuid]["metrics"].keys())


def insert_new_report(database: Database, delta_description: str, uuids, *reports) -> dict[str, Any]:
    """Insert one or more new reports in the reports collection."""
    _prepare_documents_for_insertion(database, delta_description, reports, uuids, last=True)
    report_uuids = [report["report_uuid"] for report in reports]
    database.reports.update_many({"report_uuid": {"$in": report_uuids}, "last": DOES_EXIST}, {"$unset": {"last": ""}})
    if len(reports) > 1:
        database.reports.insert_many(reports, ordered=False)
    else:
        database.reports.insert_one(reports[0])
    return dict(ok=True)


def insert_new_reports_overview(database: Database, delta_description: str, reports_overview) -> dict[str, Any]:
    """Insert a new reports overview in the reports overview collection."""
    _prepare_documents_for_insertion(database, delta_description, [reports_overview])
    database.reports_overviews.insert_one(reports_overview)
    return dict(ok=True)


def _prepare_documents_for_insertion(
    database: Database, delta_description: str, documents, uuids=None, **extra_attributes
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
        document["delta"] = dict(description=description, email=user.email)
        if uuids:
            document["delta"]["uuids"] = sorted(list(set(uuids)))
        for key, value in extra_attributes.items():
            document[key] = value


def latest_report(database: Database, data_model, report_uuid: str) -> Report | None:
    """Get latest report with this uuid."""
    report_dict = database.reports.find_one({"report_uuid": report_uuid, "last": True, "deleted": DOES_NOT_EXIST})
    if report_dict:
        return Report(data_model, report_dict)


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
            if "deleted" not in report_dict:
                report_dicts.append(report_dict)
    else:
        report_dicts = database.reports.find({"last": True, "deleted": DOES_NOT_EXIST})
    return [Report(data_model, report_dict) for report_dict in report_dicts]


def latest_reports_overview(database: Database, max_iso_timestamp: str = "") -> dict:
    """Return the latest reports overview."""
    timestamp_filter = dict(timestamp={"$lt": max_iso_timestamp}) if max_iso_timestamp else None
    overview = database.reports_overviews.find_one(timestamp_filter, sort=TIMESTAMP_DESCENDING)
    if overview:
        overview["_id"] = str(overview["_id"])
    return overview or {}


def report_exists(database: Database, report_uuid: ReportId):
    """Return whether a report with the specified report uuid exists."""
    return report_uuid in database.reports.distinct("report_uuid")
