"""Report loaders."""

import json
import logging
import pathlib

from pymongo.database import Database

from database.datamodels import default_metric_attributes, default_source_parameters, default_subject_attributes
from database.reports import insert_new_report, insert_new_reports_overview, latest_reports_overview, report_exists
from server_utilities.functions import uuid


def initialize_reports_overview(database: Database) -> None:
    """Initialize the reports overview if not present in the database."""
    # The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
    # as covered, sometimes not. It's unclear why. To prevent needless checking of the coverage report coverage
    # measurement of the last two lines and the if-statement has been turned off.
    if latest_reports_overview(database):  # pragma: no cover-behave
        logging.info("Skipping initializing reports overview; it already exists")
    else:
        logging.info("Initializing reports overview")  # pragma: no cover-behave
        insert_new_reports_overview(
            database, "{{user}} initialized the reports overview", dict(title="Reports", subtitle="")
        )  # pragma: no cover-behave


def import_report(database: Database, filename: pathlib.Path) -> None:
    """Read the report and store it in the database."""
    # The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
    # as covered, sometimes not. It's unclear why. To prevent needless checking of the coverage report coverage
    # measurement of the last two lines and the if-statement has been turned off.
    with filename.open() as json_report:
        imported_report = json.load(json_report)
    if report_exists(database, imported_report["report_uuid"]):  # pragma: no cover-behave
        logging.info("Skipping import of %s; it already exists", filename)
    else:
        import_json_report(database, imported_report)  # pragma: no cover-behave
        logging.info("Report %s imported", filename)  # pragma: no cover-behave


def import_json_report(database: Database, imported_report):
    """ Store the report given as json in the database."""
    report_to_store = dict(
        title=imported_report.get("title", "Example report"), report_uuid=imported_report["report_uuid"], subjects={}
    )
    for imported_subject in imported_report.get("subjects", []):
        subject_to_store = default_subject_attributes(database, imported_subject["type"])
        subject_to_store["metrics"] = {}  # Remove default metrics
        subject_to_store["name"] = imported_subject["name"]
        report_to_store["subjects"][uuid()] = subject_to_store
        for imported_metric in imported_subject.get("metrics", []):
            metric_to_store = default_metric_attributes(database, imported_metric["type"])
            metric_to_store.update(imported_metric)
            metric_to_store["sources"] = {}  # Sources in the example report json are lists, we transform them to dicts
            subject_to_store["metrics"][uuid()] = metric_to_store
            for imported_source in imported_metric.get("sources", []):
                source_to_store = metric_to_store["sources"][uuid()] = imported_source
                source_parameters = default_source_parameters(
                    database, imported_metric["type"], imported_source["type"]
                )
                for key, value in source_parameters.items():
                    if key not in source_to_store["parameters"]:
                        source_to_store["parameters"][key] = value
    return insert_new_report(
        database, "{{user}} imported a new report", (report_to_store, report_to_store["report_uuid"])
    )


def import_example_reports(database: Database) -> None:
    """Import the example reports."""
    example_reports_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "example-reports"
    for filename in example_reports_path.glob("example-report*.json"):
        import_report(database, filename)
