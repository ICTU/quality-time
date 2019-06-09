"""Report loaders."""

import glob
import json
import logging

from pymongo.database import Database

from ..util import uuid
from ..database.datamodels import default_subject_attributes, default_metric_attributes, \
    default_source_parameters
from ..database.reports import latest_report, insert_new_report


def import_report(database: Database, filename: str) -> None:
    """Read the report and store it in the database."""
    with open(filename) as json_report:
        imported_report = json.load(json_report)
    stored_report = latest_report(database, imported_report["report_uuid"])
    if stored_report:
        logging.info("Skipping import of %s; it already exists", filename)
        return
    report_to_store = dict(
        title=imported_report.get("title", "Quality-time"), report_uuid=imported_report["report_uuid"], subjects={})
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
    for filename in glob.glob("example-reports/example-report*.json"):
        import_report(database, filename)
