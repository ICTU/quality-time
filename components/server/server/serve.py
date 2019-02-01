"""Quality-time server."""

from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import json
import logging

import bottle
import pymongo

from . import cors  # pylint: disable=unused-import
from . import comment  # pylint: disable=unused-import
from . import report  # pylint: disable=unused-import
from . import target  # pylint: disable=unused-import
from . import measurement  # pylint: disable=unused-import
from . import datamodel  # pylint: disable=unused-import
from .route_injection_plugin import InjectionPlugin
from .util import iso_timestamp, uuid


def import_datamodel(database):
    """Read the data model store it in the database."""
    with open("datamodel.json") as json_datamodel:
        data_model = json.load(json_datamodel)
    database.datamodel.delete_many({})
    database.datamodel.insert_one(data_model)
    logging.info("Datamodel loaded")


def import_report(database):
    """Read the example report and store it in the database."""
    # Until reports can be configured via the front-end, we load an example report on start up
    # and replace the existing report in the database, if any.
    if database.reports.count_documents({}):
        return
    with open("example-report.json") as json_report:
        imported_report = json.load(json_report)
    report_to_store = dict(title="Quality-time", timestamp=iso_timestamp(), subjects={})
    for imported_subject in imported_report["subjects"]:
        subject_to_store = report_to_store["subjects"][uuid()] = dict(title=imported_subject["title"], metrics={})
        for imported_metric in imported_subject["metrics"]:
            metric_to_store = subject_to_store["metrics"][uuid()] = dict(type=imported_metric["type"], sources={})
            for imported_source in imported_metric["sources"]:
                metric_to_store["sources"][uuid()] = imported_source

    database.reports.remove({})
    database.reports.insert(report_to_store)
    stored_report = database.reports.find_one({})
    nr_subjects = len(stored_report["subjects"])
    nr_metrics = sum([len(subject["metrics"]) for subject in stored_report["subjects"].values()])
    logging.info("Report consists of %d subjects and %d metrics", nr_subjects, nr_metrics)


def serve() -> None:
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    database = pymongo.MongoClient("mongodb://root:root@localhost:27017/").quality_time_db
    logging.info("Connected to database: %s", database)
    logging.info("Measurements collection has %d measurements", database.measurements.count_documents({}))
    injection_plugin = InjectionPlugin(value=database, keyword="database")
    bottle.install(injection_plugin)
    import_datamodel(database)
    import_report(database)
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)


if __name__ == "__main__":
    serve()
