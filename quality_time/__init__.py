"""Entry point and routes for Quality-time."""

import logging

from bottle import request, route, run

from .metrics import *
from .sources import *
from .metric import metric_registered_for
from .source import source_registered_for
from .type import MeasurementResponse


__title__ = "Quality time"
__version__ = "0.1.0"

METRIC_SOURCE_ID = {
    (FailedJobs, Jenkins): "failed_jobs",
    (FailedTests, JUnit): "failures",
    (FailedTests, SonarQube): "test_failures",
    (Jobs, Jenkins): "jobs",
    (NonCommentedLinesOfCode, SonarQube): "ncloc",
    (LinesOfCode, SonarQube): "lines",
    (Tests, JUnit): "tests",
    (Tests, SonarQube): "tests",
    (Version, SonarQube): "version",
    (Violations, SonarQube): "violations"
}

def process(metric, source, urls, components):
    """Process."""
    metric_id = METRIC_SOURCE_ID[(metric, source)]
    response = source.get(metric_id, urls, components)
    measurements = [source_response["measurement"] for source_response in response["source_responses"]]
    measurement, calculation_error = metric.safely_sum(measurements)
    response.update(dict(metric=metric.name(), calculation_error=calculation_error, measurement=measurement))
    return response


@route("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str) -> MeasurementResponse:
    """Handler for the get-metric-from-source API."""
    logging.info(request)
    metric = metric_registered_for(metric_name)
    source = source_registered_for(source_name)
    urls = request.query.getall("url")  # pylint: disable=no-member
    components = request.query.getall("component")  # pylint: disable=no-member
    return process(metric, source, urls, components)


def quality_time():
    """Main entry point."""
    logging.getLogger().setLevel(logging.INFO)
    run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)
