"""API for metrics."""

import bottle


@bottle.get("/metric/<metric_name>")
def get_metric(metric_name: str, database):
    """Return the metric."""
    metric = database.metrics.find_one({"metric": metric_name})
    metric["_id"] = str(metric["_id"])
    return metric
