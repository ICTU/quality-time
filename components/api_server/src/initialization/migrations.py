"""Database migrations."""

import logging

import pymongo
from pymongo.collection import Collection
from pymongo.database import Database

from shared.model.metric import Metric


def perform_migrations(database: Database) -> None:  # pragma: no feature-test-cover
    """Perform database migrations."""
    for report in database.reports.find(filter={"last": True, "deleted": {"$exists": False}}):
        change_accessibility_violation_metrics_to_violations(database, report)
        fix_branch_parameters_without_value(database, report)
        add_source_parameter_hash(database, report)


def change_accessibility_violation_metrics_to_violations(  # pragma: no feature-test-cover
    database: Database, report
) -> None:
    """Replace accessibility metrics with the violations metric."""
    # Added after Quality-time v5.5.0, see https://github.com/ICTU/quality-time/issues/562
    report_uuid = report["report_uuid"]
    logging.info("Checking report for accessibility metrics: %s", report_uuid)
    changed = False
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if metric["type"] == "accessibility":
                change_accessibility_violations_metric_to_violations(metric)
                changed = True
    if changed:
        logging.info("Updating report to change its accessibility metrics to violations metrics: %s", report_uuid)
        replace_document(database.reports, report)
    else:
        logging.info("No accessibility metrics found in report: %s", report_uuid)


def change_accessibility_violations_metric_to_violations(metric: dict) -> None:  # pragma: no feature-test-cover
    """Change the accessibility violations metric to violations metric."""
    metric["type"] = "violations"
    if not metric.get("name"):
        metric["name"] = "Accessibility violations"
    if not metric.get("unit"):
        metric["unit"] = "accessibility violations"


def fix_branch_parameters_without_value(database: Database, report) -> None:  # pragma: no feature-test-cover
    """Set the branch parameter of sources to 'master' (the previous default) if they have no value."""
    # Added after Quality-time v5.11.0, see https://github.com/ICTU/quality-time/issues/8045
    report_uuid = report["report_uuid"]
    logging.info("Checking report for sources with empty branch parameters: %s", report_uuid)
    changed = False
    for source in sources_with_branch_parameter(report):
        if not source["parameters"].get("branch"):
            source["parameters"]["branch"] = "master"
            changed = True
    if changed:
        logging.info("Updating report to change sources with empty branch parameter: %s", report_uuid)
        replace_document(database.reports, report)
    else:
        logging.info("No sources with empty branch parameters found in report: %s", report_uuid)


METRICS_WITH_SOURCES_WITH_BRANCH_PARAMETER = {
    "commented_out_code": ["sonarqube"],
    "complex_units": ["sonarqube"],
    "duplicated_lines": ["sonarqube"],
    "loc": ["sonarqube"],
    "long_units": ["sonarqube"],
    "many_parameters": ["sonarqube"],
    "remediation_effort": ["sonarqube"],
    "security_warnings": ["sonarqube"],
    "software_version": ["sonarqube"],
    "source_up_to_dateness": ["azure_devops", "gitlab", "sonarqube"],
    "suppressed_violations": ["sonarqube"],
    "tests": ["sonarqube"],
    "todo_and_fixme_comments": ["sonarqube"],
    "uncovered_branches": ["sonarqube"],
    "uncovered_lines": ["sonarqube"],
    "violations": ["sonarqube"],
}


def sources_with_branch_parameter(report: dict):  # pragma: no feature-test-cover
    """Return the sources with a branch parameter."""
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if metric["type"] in METRICS_WITH_SOURCES_WITH_BRANCH_PARAMETER:
                for source in metric.get("sources", {}).values():
                    if source["type"] in METRICS_WITH_SOURCES_WITH_BRANCH_PARAMETER[metric["type"]]:
                        yield source


def add_source_parameter_hash(database: Database, report) -> None:  # pragma: no feature-test-cover
    """Add source parameter hashes to the latest measurements."""
    # Added after Quality-time v5.12.0, see https://github.com/ICTU/quality-time/issues/8736
    for subject in report["subjects"].values():
        for metric_uuid, metric in subject["metrics"].items():
            latest_measurement = database.measurements.find_one(
                filter={"metric_uuid": metric_uuid},
                sort=[("start", pymongo.DESCENDING)],
            )
            if not latest_measurement:
                continue
            if latest_measurement.get("source_parameter_hash"):
                continue
            latest_measurement["source_parameter_hash"] = Metric({}, metric, metric_uuid).source_parameter_hash()
            replace_document(database.measurements, latest_measurement)


def replace_document(collection: Collection, document) -> None:  # pragma: no feature-test-cover
    """Replace the document in the collection."""
    document_id = document["_id"]
    del document["_id"]
    collection.replace_one({"_id": document_id}, document)
