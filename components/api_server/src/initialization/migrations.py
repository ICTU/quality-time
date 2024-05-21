"""Database migrations."""

import logging

from pymongo.database import Database


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
