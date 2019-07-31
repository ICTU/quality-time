"""Reports collection."""

from pymongo.database import Database
from shared.database.reports import latest_report


def latest_reports(database: Database):
    """Return all latest reports in the reports collection."""
    report_uuids = database.reports.distinct("report_uuid")
    reports = []
    for report_uuid in report_uuids:
        report = latest_report(database, report_uuid)
        if report and "deleted" not in report:
            report["_id"] = str(report["_id"])
            reports.append(report)
    return reports
