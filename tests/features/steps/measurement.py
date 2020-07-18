"""Step implementations for measurement."""

from asserts import assert_true


@when("the collector gets the metrics to measure")
def get_metrics(context):
    """Get the metrics to measure from the server."""
    context.metrics = context.get("metrics")


@then("the metric needs to be measured")
def check_metrics(context):
    """Check that the metric needs to be measured."""
    assert_true(context.uuid["metric"] in context.metrics.keys())
