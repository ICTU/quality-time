"""Report loaders."""

import json
import logging
import os.path
import pathlib

from pymongo.database import Database

from database.datamodels import default_subject_attributes, default_metric_attributes, default_source_parameters
from database.reports import latest_report, insert_new_report, latest_reports_overview, insert_new_reports_overview
from utilities.functions import uuid


def initialize_reports_overview(database: Database) -> None:
    """Initialize the reports overview if not present in the database."""
    if latest_reports_overview(database):
        logging.info("Skipping initializing reports overview; it already exists")
    else:
        logging.info("Initializing reports overview")
        insert_new_reports_overview(database, dict(title="Reports", subtitle=""))


def import_report(database: Database, filename: str) -> None:
    """Read the report and store it in the database."""
    with open(filename) as json_report:
        imported_report = json.load(json_report)
    stored_report = latest_report(database, imported_report["report_uuid"])
    if stored_report:
        logging.info("Skipping import of %s; it already exists", filename)
        return
    report_to_store = dict(
        title=imported_report.get("title", "Example report"), report_uuid=imported_report["report_uuid"], subjects={})
    for imported_subject in imported_report["subjects"]:
        subject_to_store = default_subject_attributes(database, imported_subject["type"])
        subject_to_store["metrics"] = dict()  # Remove default metrics
        subject_to_store["name"] = imported_subject["name"]
        report_to_store["subjects"][uuid()] = subject_to_store
        for imported_metric in imported_subject["metrics"]:
            metric_to_store = default_metric_attributes(
                database, imported_report["report_uuid"], imported_metric["type"])
            metric_to_store.update(imported_metric)
            metric_to_store["sources"] = {}  # Sources in the example report json are lists, we transform them to dicts
            subject_to_store["metrics"][uuid()] = metric_to_store
            for imported_source in imported_metric["sources"]:
                source_to_store = metric_to_store["sources"][uuid()] = imported_source
                source_parameters = default_source_parameters(
                    database, imported_metric["type"], imported_source["type"])
                for key, value in source_parameters.items():
                    if key not in source_to_store["parameters"]:
                        source_to_store["parameters"][key] = value

    insert_new_report(database, report_to_store)
    logging.info("Report %s imported", filename)


def import_example_reports(database: Database) -> None:
    """Import the example reports."""
    example_reports_path = pathlib.Path(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "example-reports").resolve()
    for filename in example_reports_path.glob("example-report*.json"):
        import_report(database, filename)
