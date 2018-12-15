"""Entry points and routes for Quality-time."""

import logging
from typing import cast, Type

import bottle

from .metrics import *
from .sources import *
from .metric import Metric
from .report_updater import run
from .source import Source
from .type import Response


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str) -> Response:
    """Handler for the get-metric-from-source API."""
    logging.info(bottle.request)
    query = bottle.request.query
    metric = cast(Type[Metric], Metric.subclass_for_api(metric_name))(query)
    source = cast(Type[Source], Source.subclass_for_api(f"{source_name}_{metric_name}"))(query)
    urls = query.getall("url")  # pylint: disable=no-member
    components = query.getall("component")  # pylint: disable=no-member
    return metric.get(source.get(dict(request_url=request.url, urls=urls, components=components)))


def metric_source_facade():
    """Start the metric-source API which functions as a facade to get metric data from different sources in a
    consistent manner."""
    logging.getLogger().setLevel(logging.INFO)
    bottle.run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)


def update_reports():
    """Update the reports."""
    logging.getLogger().setLevel(logging.INFO)
    run()
