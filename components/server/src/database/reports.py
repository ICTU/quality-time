"""Reports collection."""

import pymongo
from pymongo.database import Database

from model.report import Report
from server_utilities.functions import iso_timestamp

from .filters import DOES_NOT_EXIST


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
