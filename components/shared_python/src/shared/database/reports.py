"""Reports collection."""

from typing import Any

import pymongo
from pymongo.database import Database

from shared.database.filters import DOES_EXIST
from shared.utils.functions import iso_timestamp
from shared.utils.type import ReportId
from . import sessions


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


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


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


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
