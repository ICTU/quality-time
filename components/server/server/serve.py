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
from . import metric  # pylint: disable=unused-import
from .route_injection_plugin import InjectionPlugin
from .util import iso_timestamp


def import_metrics(database):
    """Read the metric types and store them in the database."""
    with open("metrics.json") as json_metrics:
        metrics = json.load(json_metrics)
    database.metrics.remove({})
    database.metrics.insert(metrics["metrics"])
    nr_stored_metrics = database.metrics.count_documents({})
    logging.info("Metrics collection has %d metrics", nr_stored_metrics)


def import_report(database):
    """Read the example report and store it in the database."""
    # Until reports can be configured via the front-end, we load an example report on start up
    # and replace the existing report in the database, if any.
    if database.reports.count_documents({}):
        return
    with open("example-report.json") as json_report:
        report = json.load(json_report)
    report["title"] = "Quality-time"
    report["timestamp"] = "2019-01-01T00:00:00+00:00" or iso_timestamp()
    database.reports.remove({})
    database.reports.insert(report)
    stored_report = database.reports.find_one({})
    nr_subjects = len(stored_report["subjects"])
    nr_metrics = sum([len(subject["metrics"]) for subject in stored_report["subjects"]])
    logging.info("Report consists of %d subjects and %d metrics", nr_subjects, nr_metrics)


def serve() -> None:
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    database = pymongo.MongoClient("mongodb://root:root@localhost:27017/").quality_time_db
    logging.info("Connected to database: %s", database)
    logging.info("Measurements collection has %d measurements", database.measurements.count_documents({}))
    injection_plugin = InjectionPlugin(value=database, keyword="database")
    bottle.install(injection_plugin)
    import_metrics(database)
    import_report(database)
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)


if __name__ == "__main__":
    serve()
