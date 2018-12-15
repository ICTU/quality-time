"""Entry point and routes for Quality-time."""

import logging
from typing import cast, Type

from bottle import request, route, run

from .metrics import *
from .sources import *
from .metric import Metric
from .source import Source
from .type import Response


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<metric_name>/<source_name>")
def get(metric_name: str, source_name: str) -> Response:
    """Handler for the get-metric-from-source API."""
    logging.info(request)
    query = request.query
    urls = query.getall("url")
    components = query.getall("component")
    metric = cast(Type[Metric], Metric.subclass_for_api(metric_name))(query)
    source = cast(
        Type[Source], Source.subclass_for_api(f"{source_name}_{metric_name}"))(query, urls=urls, components=components)
    return metric.get(source.get(dict(request_url=request.url)))


def quality_time():
    """Main entry point."""
    logging.getLogger().setLevel(logging.INFO)
    run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)
