"""Database migrations."""

from collections.abc import Sequence

import pymongo
from pymongo.collection import Collection
from pymongo.database import Database

from shared.model.metric import Metric

from utils.log import get_logger


def perform_migrations(database: Database) -> None:
    """Perform database migrations."""
    logger = get_logger()
    for report in database.reports.find(filter={"last": True, "deleted": {"$exists": False}}):
        report_uuid = report["report_uuid"]
        logger.info("Checking report %s for necessary updates", report_uuid)
        if any(
            changes := [
                change_accessibility_violation_metrics_to_violations(report),
                fix_branch_parameters_without_value(report),
                remove_test_cases_manual_number(report),
                change_ci_subject_types_to_development_environment(report),
                change_sonarqube_parameters(report),
                change_unmerged_branches_metrics_to_inactive_branches(report),
                change_inactive_branches_project_parameter_to_project_or_group(report),
            ]
        ):
            change_description = " and to ".join([change for change in changes if change])
            logger.info("Updating report %s to %s", report_uuid, change_description)
            replace_document(database.reports, report)
        logger.info("Checking report %s for necessary measurement updates", report_uuid)
        count = add_source_parameter_hash_to_latest_measurement(database, report)
        logger.info("Updated %s measurements for report %s", count, report_uuid)


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


def remove_test_cases_manual_number(report) -> str:
    """Remove manual number sources from test cases metrics."""
    # Added after Quality-time v5.15.0, see https://github.com/ICTU/quality-time/issues/9793
    change = ""
    for metric in metrics(report, metric_types=("test_cases",)):
        for source_uuid, source in metric.get("sources", {}).copy().items():
            if source["type"] == "manual_number":
                del metric["sources"][source_uuid]
                change = "remove manual number sources from test cases metrics"
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


def change_sonarqube_parameters(report) -> str:
    """Replace the SonarQube parameters to adapt to the new (SonarQube 10.2) issue structure.

    Return a description of the change, if any.
    """
    # Added after Quality-time v5.13.0, see https://github.com/ICTU/quality-time/issues/8354
    if change_sonarqube_severities(report) or change_sonarqube_types(report) or change_sonarqube_security_types(report):
        return "change the SonarQube parameters"
    return ""


def change_sonarqube_severities(report) -> bool:
    """Change the SonarQube severities parameter to the new values and rename it to impact_severities."""
    # Severity mapping conform https://docs.sonarsource.com/sonarqube/latest/user-guide/issues/#severity-mapping:
    value_mapping = {"blocker": "high", "critical": "high", "major": "medium", "minor": "low", "info": "low"}
    metric_types = ("security_warnings", "suppressed_violations", "violations")
    return change_sonarqube_parameter(report, metric_types, "severities", "impact_severities", value_mapping)


def change_sonarqube_types(report) -> bool:
    """Change the SonarQube types parameter to the new values and rename it to impacted_software_qualities."""
    value_mapping = {"bug": "reliability", "vulnerability": "security", "code_smell": "maintainability"}
    metric_types = ("suppressed_violations", "violations")
    return change_sonarqube_parameter(report, metric_types, "types", "impacted_software_qualities", value_mapping)


def change_sonarqube_security_types(report) -> bool:
    """Change the SonarQube security types parameter to the new values."""
    value_mapping = {"security_hotspot": "security hotspot", "vulnerability": "issue with security impact"}
    metric_types = ("security_warnings",)
    return change_sonarqube_parameter(report, metric_types, "security_types", "security_types", value_mapping)


def change_sonarqube_parameter(
    report, metric_types: Sequence[str], old_parameter_name: str, new_parameter_name: str, value_mapping: dict[str, str]
) -> bool:
    """Change the values of the specified parameter. Also rename the parameter if the old and new name differ."""
    changed = False
    for source in sources(report, metric_types=metric_types, source_type="sonarqube", parameter=old_parameter_name):
        old_values = source["parameters"][old_parameter_name]
        log_unknown_parameter_values(value_mapping, old_values, old_parameter_name, report)
        if new_values := new_parameter_values(value_mapping, old_values):
            source["parameters"][new_parameter_name] = new_values
            changed = True
        if new_parameter_name != old_parameter_name:
            del source["parameters"][old_parameter_name]
            changed = True
    return changed


def change_unmerged_branches_metrics_to_inactive_branches(report) -> str:
    """Change unmerged branches metrics to inactive branches metrics."""
    # Added after Quality-time v5.19.0, see https://github.com/ICTU/quality-time/issues/1253
    change = ""
    for metric in metrics(report, ["unmerged_branches"]):
        metric["type"] = "inactive_branches"
        for source in metric.get("sources", {}).values():
            source["parameters"]["branch_merge_status"] = ["unmerged"]
        if not metric.get("name"):
            metric["name"] = "Unmerged branches"
        change = "metric type 'unmerged_branches' to 'inactive_branches'"
    return change


def change_inactive_branches_project_parameter_to_project_or_group(report) -> str:
    """Change the parameter 'project' of the metric 'inactive branches' to 'project_or_group'."""
    # Added after Quality-time v5.37.0, see https://github.com/ICTU/quality-time/issues/7991
    change = ""
    for metric in metrics(report, ["inactive_branches"]):
        for source in metric.get("sources", {}).values():
            if source["type"] == "gitlab" and "project" in source["parameters"]:
                source["parameters"]["project_or_group"] = source["parameters"]["project"]
                del source["parameters"]["project"]
                change = (
                    "the parameter 'project' of source type 'gitlab' to 'project_or_group' "
                    "for metric type 'inactive_branches'"
                )
    return change


def log_unknown_parameter_values(value_mapping: dict[str, str], old_values: list[str], value_type: str, report) -> None:
    """Log old parameter values that do not exist in the mapping."""
    known_values = list(value_mapping.keys()) + list(value_mapping.values())
    if unknown_values := [old_value for old_value in old_values if old_value not in known_values]:
        message = "Ignoring one or more unknown SonarQube parameter values of type '%s' in report %s: %s"
        logger = get_logger()
        logger.warning(message, value_type, report["report_uuid"], ", ".join(unknown_values))


def new_parameter_values(value_mapping: dict[str, str], old_values: list[str]) -> list[str]:
    """Return the new values for each of the old values that exist in the mapping."""
    return sorted({value_mapping[old_value] for old_value in old_values if old_value in value_mapping})


def sources(report, metric_types: Sequence[str], source_type: str, parameter: str):
    """Yield the sources in the report, filtered by metric type, source type, and parameter."""
    for metric in metrics(report, metric_types):
        for source in metric.get("sources", {}).values():
            if source["type"] == source_type and parameter in source["parameters"]:
                yield source


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
