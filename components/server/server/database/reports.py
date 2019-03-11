"""Reports collection."""

import pymongo

from ..util import iso_timestamp


def latest_reports(max_iso_timestamp: str, database):
    """Return all latest reports in the reports collection."""
    report_uuids = database.reports.distinct("report_uuid")
    reports = []
    for report_uuid in report_uuids:
        report = database.reports.find_one(
            filter={"report_uuid": report_uuid, "timestamp": {"$lt": max_iso_timestamp}},
            sort=[("timestamp", pymongo.DESCENDING)])
        if report and not "deleted" in report:
            report["_id"] = str(report["_id"])
            # Include a summary of the current measurement values
            summarize_report(report, database)
            reports.append(report)
    return reports


def summarize_report(report, database) -> None:
    """Add a summary of the measurements to each subject."""
    from .measurements import latest_measurement  # Prevent circular import
    total_red, total_green, total_yellow, total_grey = 0, 0, 0, 0
    for subject in report.get("subjects", {}).values():
        red, green, yellow, grey = 0, 0, 0, 0
        for metric_uuid in subject.get("metrics", {}).keys():
            latest = latest_measurement(metric_uuid, database)
            if latest:
                if latest["value"] is None:
                    yellow += 1
                    total_yellow += 1
                elif latest["status"] == "target_met":
                    green += 1
                    total_green += 1
                elif latest["status"] == "debt_target_met":
                    grey += 1
                    total_grey += 1
                else:
                    red += 1
                    total_red += 1
            else:
                yellow += 1
                total_yellow += 1
        subject["summary"] = dict(red=red, green=green, yellow=yellow, grey=grey)
    report["summary"] = dict(red=total_red, green=total_green, yellow=total_yellow, grey=total_grey)


def latest_report(report_uuid: str, database):
    """Return the latest report for the specified report uuid."""
    return database.reports.find_one(filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])


def latest_metric(metric_uuid: str, max_iso_timestamp: str, database):
    """Return the latest metric with the specified uuid."""
    reports = latest_reports(max_iso_timestamp, database)
    for report in reports:
        for subject in report.get("subjects", {}).values():
            metrics = subject.get("metrics", {})
            if metric_uuid in metrics:
                return metrics[metric_uuid]
    return None


def insert_new_report(report, database):
    """Insert a new report in the reports collection."""
    if "_id" in report:
        del report["_id"]
    report["timestamp"] = iso_timestamp()
    database.reports.insert(report)
    return dict(ok=True)
