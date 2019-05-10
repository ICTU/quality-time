"""Quality-time server."""

from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import glob
import json
import logging
import os

import bottle
import ldap
import pymongo
from pymongo.database import Database

from . import cors  # pylint: disable=unused-import
from .routes import report, measurement, datamodel, auth  # pylint: disable=unused-import
from .route_injection_plugin import InjectionPlugin
from .util import uuid
from .database.datamodels import insert_new_datamodel, default_subject_attributes, default_metric_attributes, \
    default_source_parameters, latest_datamodel
from .database.reports import latest_report, insert_new_report


def import_datamodel(database: Database) -> None:
    """Read the data model and store it in the database."""
    with open("datamodel.json") as json_datamodel:
        data_model = json.load(json_datamodel)
    latest = latest_datamodel(database)
    if latest:
        del latest["timestamp"]
        del latest["_id"]
        if data_model == latest:
            logging.info("Skipping loading the datamodel; it is unchanged")
            return
    insert_new_datamodel(database, data_model)
    logging.info("Datamodel loaded")


def import_report(database: Database, filename: str) -> None:
    """Read the report and store it in the database."""
    with open(filename) as json_report:
        imported_report = json.load(json_report)
    report_uuid = imported_report["report_uuid"]
    stored_report = latest_report(database, report_uuid)
    if stored_report:
        logging.info("Skipping import of %s; it already exists", filename)
        return
    report_to_store = dict(
        title=imported_report.get("title", "Quality-time"), report_uuid=report_uuid, subjects={})
    for imported_subject in imported_report["subjects"]:
        subject_to_store = report_to_store["subjects"][uuid()] = default_subject_attributes(
            database, imported_subject["type"])
        subject_to_store["metrics"] = dict()  # Remove default metrics
        subject_to_store["name"] = imported_subject["name"]
        for imported_metric in imported_subject["metrics"]:
            metric_type = imported_metric["type"]
            metric_to_store = subject_to_store["metrics"][uuid()] = default_metric_attributes(
                database, report_uuid, metric_type)
            metric_to_store.update(imported_metric)
            metric_to_store["sources"] = {}  # Sources in the example report json are lists, we transform them to dicts
            for imported_source in imported_metric["sources"]:
                source_to_store = metric_to_store["sources"][uuid()] = imported_source
                source_parameters = default_source_parameters(database, metric_type, imported_source["type"])
                for key, value in source_parameters.items():
                    if key not in source_to_store["parameters"]:
                        source_to_store["parameters"][key] = value

    insert_new_report(database, report_to_store)
    logging.info("Report %s imported", filename)


def import_example_reports(database: Database) -> None:
    """Import the example reports."""
    for filename in glob.glob("example-reports/example-report*.json"):
        import_report(database, filename)


def serve() -> None:
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    logging.info("Connected to database: %s", database)
    logging.info("Measurements collection has %d measurements", database.measurements.count_documents({}))
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    logging.info("Initializing LDAP server at %s", ldap_url)
    ldap_server = ldap.initialize(ldap_url)
    ldap_injection_plugin = InjectionPlugin(value=ldap_server, keyword="ldap_server")
    bottle.install(ldap_injection_plugin)
    database_injection_plugin = InjectionPlugin(value=database, keyword="database")
    bottle.install(database_injection_plugin)
    import_datamodel(database)
    import_example_reports(database)
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)
