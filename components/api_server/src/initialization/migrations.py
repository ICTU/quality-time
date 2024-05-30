"""Database migrations."""

from collections.abc import Sequence
import logging

import pymongo
from pymongo.collection import Collection
from pymongo.database import Database

from shared.model.metric import Metric


def perform_migrations(database: Database) -> None:
    """Perform database migrations."""
    for report in database.reports.find(filter={"last": True, "deleted": {"$exists": False}}):
        report_uuid = report["report_uuid"]
        logging.info("Checking report %s for necessary updates", report_uuid)
        if any(
            changes := [
                change_accessibility_violation_metrics_to_violations(report),
                fix_branch_parameters_without_value(report),
                change_ci_subject_types_to_development_environment(report),
            ]
        ):
            change_description = " and to ".join([change for change in changes if change])
            logging.info("Updating report %s to %s", report_uuid, change_description)
            replace_document(database.reports, report)
        logging.info("Checking report %s for necessary measurement updates", report_uuid)
        count = add_source_parameter_hash_to_latest_measurement(database, report)
        logging.info("Updated %s measurements for report %s", count, report_uuid)


def change_accessibility_violation_metrics_to_violations(report) -> str:
    """Replace accessibility metrics with violations metrics. Return a description of the change, if any."""
    # Added after Quality-time v5.5.0, see https://github.com/ICTU/quality-time/issues/562
    change = ""
    for metric in metrics(report, metric_types=("accessibility",)):
        metric["type"] = "violations"
        if not metric.get("name"):
            metric["name"] = "Accessibility violations"
        if not metric.get("unit"):
            metric["unit"] = "accessibility violations"
        change = "change its accessibility metrics to violations metrics"
    return change


def fix_branch_parameters_without_value(report) -> str:
    """Set the branch parameter of sources to 'master' (the previous default) if they have no value.

    Return a description of the change, if any.
    """
    # Added after Quality-time v5.11.0, see https://github.com/ICTU/quality-time/issues/8045
    change = ""
    for source in sources_with_branch_parameter(report):
        if not source["parameters"].get("branch"):
            source["parameters"]["branch"] = "master"
            change = "change sources with empty branch parameter"
    return change


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


def sources_with_branch_parameter(report: dict):
    """Return the sources with a branch parameter."""
    for metric in metrics(report, list(METRICS_WITH_SOURCES_WITH_BRANCH_PARAMETER.keys())):
        for source in metric.get("sources", {}).values():
            if source["type"] in METRICS_WITH_SOURCES_WITH_BRANCH_PARAMETER[metric["type"]]:
                yield source


def change_ci_subject_types_to_development_environment(report) -> str:
    """Change the CI subject type to development environment. Return a description of the change, if any."""
    # Added after Quality-time v5.13.0, see https://github.com/ICTU/quality-time/issues/3130
    change = ""
    for subject in subjects(report, subject_type="ci"):
        subject["type"] = "development_environment"
        if not subject.get("name"):
            subject["name"] = "CI-environment"
        if not subject.get("description"):
            subject["description"] = "A continuous integration environment."
        change = "change subjects with type 'ci'"
    return change


def add_source_parameter_hash_to_latest_measurement(database: Database, report) -> int:
    """Add source parameter hashes to the latest measurements. Return the number of measurements changed."""
    # Added after Quality-time v5.12.0, see https://github.com/ICTU/quality-time/issues/8736
    count = 0
    for subject in subjects(report):
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
            count += 1
    return count


def metrics(report, metric_types: Sequence[str] | None = None):
    """Yield the metrics in the report, optionally filtered by metric type."""
    for subject in subjects(report):
        for metric in subject["metrics"].values():
            if not metric_types or metric["type"] in metric_types:
                yield metric


def subjects(report, subject_type: str | None = None):
    """Yield the subjects in the report, optionally filtered by subject type."""
    for subject in report["subjects"].values():
        if not subject_type or subject["type"] == subject_type:
            yield subject


def replace_document(collection: Collection, document) -> None:
    """Replace the document in the collection."""
    document_id = document["_id"]
    del document["_id"]
    collection.replace_one({"_id": document_id}, document)
