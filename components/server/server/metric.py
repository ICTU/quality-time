"""API for metrics."""

import logging

import bottle


@bottle.get("/metric/<metric_name>")
def get_metric(metric_name: str, database):
    """Return the metric."""
    logging.info(bottle.request)
    metric = database.metrics.find_one({"metric": metric_name})
    metric["_id"] = str(metric["_id"])
    return metric
