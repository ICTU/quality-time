"""Database initialization."""

import logging
import os

import pymongo
from pymongo.database import Database

from shared.initialization.database import client

from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview
from .secrets import initialize_secrets


def init_database() -> Database:  # pragma: no feature-test-cover
    """Initialize the database contents."""
    db_client = client()
    set_feature_compatibility_version(db_client.admin)
    database = db_client.quality_time_db
    logging.info("Connected to database: %s", database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    create_indexes(database)
    import_datamodel(database)
    initialize_secrets(database)
    initialize_reports_overview(database)
    perform_migrations(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)
    return database


def set_feature_compatibility_version(admin_database: Database) -> None:
    """Set the feature compatibility version to the current MongoDB version to prepare for upgrade to the next version.

    See https://docs.mongodb.com/manual/reference/command/setFeatureCompatibilityVersion/
    """
    admin_database.command("setFeatureCompatibilityVersion", "6.0", confirm=True)


def create_indexes(database: Database) -> None:
    """Create any indexes."""
    database.datamodels.create_index("timestamp")
    database.reports.create_index([("timestamp", pymongo.ASCENDING), ("report_uuid", pymongo.ASCENDING)])
    database.users.create_index("username", unique=True)
    period_index = pymongo.IndexModel([("start", pymongo.ASCENDING), ("end", pymongo.DESCENDING)])
    latest_measurement_index = pymongo.IndexModel([("metric_uuid", pymongo.ASCENDING), ("start", pymongo.DESCENDING)])
    latest_successful_measurement_index = pymongo.IndexModel(
        [("metric_uuid", pymongo.ASCENDING), ("has_error", pymongo.ASCENDING), ("start", pymongo.DESCENDING)],
    )
    database.measurements.create_indexes([period_index, latest_measurement_index, latest_successful_measurement_index])


def perform_migrations(database: Database) -> None:  # pragma: no feature-test-cover
    """Perform database migrations."""
    change_accessibility_violation_metrics_to_violations(database)
    fix_branch_parameters_without_value(database)


def change_accessibility_violation_metrics_to_violations(database: Database) -> None:  # pragma: no feature-test-cover
    """Replace accessibility metrics with the violations metric."""
    # Added after Quality-time v5.5.0, see https://github.com/ICTU/quality-time/issues/562
    for report in database.reports.find(filter={"last": True, "deleted": {"$exists": False}}):
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
            replace_report(database, report)
        else:
            logging.info("No accessibility metrics found in report: %s", report_uuid)


def change_accessibility_violations_metric_to_violations(metric: dict) -> None:  # pragma: no feature-test-cover
    """Change the accessibility violations metric to violations metric."""
    metric["type"] = "violations"
    if not metric.get("name"):
        metric["name"] = "Accessibility violations"
    if not metric.get("unit"):
        metric["unit"] = "accessibility violations"


def fix_branch_parameters_without_value(database: Database) -> None:  # pragma: no feature-test-cover
    """Set the branch parameter of sources to 'master' (the previous default) if they have no value."""
    # Added after Quality-time v5.11.0, see https://github.com/ICTU/quality-time/issues/8045
    for report in database.reports.find(filter={"last": True, "deleted": {"$exists": False}}):
        report_uuid = report["report_uuid"]
        logging.info("Checking report for sources with empty branch parameters: %s", report_uuid)
        changed = False
        for source in sources_with_branch_parameter(report):
            if not source["parameters"].get("branch"):
                source["parameters"]["branch"] = "master"
                changed = True
        if changed:
            logging.info("Updating report to change sources with empty branch parameter: %s", report_uuid)
            replace_report(database, report)
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


def replace_report(database: Database, report) -> None:  # pragma: no feature-test-cover
    """Replace the report in the database."""
    report_id = report["_id"]
    del report["_id"]
    database.reports.replace_one({"_id": report_id}, report)
