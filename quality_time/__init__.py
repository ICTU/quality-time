"""Entry point and routes for Quality-time."""

import logging
from typing import cast, Type

from bottle import request, route, run

from .metrics import *
from .sources import *
from .metric import Metric
from .source import Source
from .type import MeasurementResponse


__title__ = "Quality time"
__version__ = "0.1.0"


METRIC_SOURCE_ID = {
    (FailedJobs, Gitlab): "failed_jobs",
    (FailedJobs, Jenkins): "failed_jobs",
    (FailedTests, JUnit): "failures",
    (FailedTests, SonarQube): "test_failures",
    (Jobs, Gitlab): "jobs",
    (Jobs, Jenkins): "jobs",
    (NCLOC, SonarQube): "ncloc",
    (LOC, SonarQube): "lines",
    (Tests, JUnit): "tests",
    (Tests, SonarQube): "tests",
    (Version, Gitlab): "version",
    (Version, Jenkins): "version",
    (Version, SonarQube): "version",
    (Violations, SonarQube): "violations"
}


@route("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str) -> MeasurementResponse:
    """Handler for the get-metric-from-source API."""
    logging.info(request)
    metric = cast(Type[Metric], Metric.subclass_for_api(metric_name))(request)
    source = cast(Type[Source], Source.subclass_for_api(source_name))(request)
    metric_id = METRIC_SOURCE_ID[(metric.__class__, source.__class__)]
    response = source.get(metric_id)
    measurements = [source_response["measurement"] for source_response in response["source_responses"]]
    response.update(metric.get(measurements))
    return response


def quality_time():
    """Main entry point."""
    logging.getLogger().setLevel(logging.INFO)
    run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)
