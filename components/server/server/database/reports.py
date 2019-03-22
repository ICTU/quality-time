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
    status_color_mapping = dict(target_met="green", debt_target_met="grey", target_not_met="red")
    summary = dict(red=0, green=0, yellow=0, grey=0)
    summary_by_subject = dict()
    summary_by_tag = dict()
    for subject_uuid, subject in report.get("subjects", {}).items():
        for metric_uuid, metric in subject.get("metrics", {}).items():
            latest = latest_measurement(metric_uuid, database)
            color = status_color_mapping.get(latest["status"], "yellow") if latest else "yellow"
            summary[color] += 1
            summary_by_subject.setdefault(subject_uuid, dict(red=0, green=0, yellow=0, grey=0))[color] += 1
            for tag in metric["tags"]:
                summary_by_tag.setdefault(tag, dict(red=0, green=0, yellow=0, grey=0))[color] += 1
    report["summary"] = summary
    report["summary_by_subject"] = summary_by_subject
    report["summary_by_tag"] = summary_by_tag


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
