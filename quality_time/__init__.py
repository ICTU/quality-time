"""Entry point and routes for Quality-time."""

import logging

from bottle import request, route, run

from . import metrics, sources  # pylint: disable=unused-import
from .metric import metric_registered_for
from .source import source_registered_for
from .type import MeasurementResponse


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str) -> MeasurementResponse:
    """Handler for the get-metric-from-source API."""
    logging.info(request)
    metric = metric_registered_for(metric_name)
    source = source_registered_for(source_name)
    urls = request.query.getall("url")  # pylint: disable=no-member
    components = request.query.getall("component")  # pylint: disable=no-member
    return source.get(metric, urls, components)


def quality_time():
    """Main entry point."""
    logging.getLogger().setLevel(logging.INFO)
    run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)
