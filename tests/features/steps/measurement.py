"""Step implementations for measurement."""

from asserts import assert_true


@when("the collector gets the metrics to measure")
def get_metrics(context):
    """Get the metrics to measure from the server."""
    context.metrics = context.get("metrics")


@when('the collector measures "{number}"')
def measure(context, number):
    """Post the measurement."""
    context.post(
        "measurements",
        json=dict(
            metric_uuid=context.uuid["metric"],
            sources=[
                dict(source_uuid=context.uuid["source"], parse_error=None, connection_error=None, value=number,
                     total="100")]))


@then("the metric needs to be measured")
def check_metrics(context):
    """Check that the metric needs to be measured."""
    assert_true(context.uuid["metric"] in context.metrics.keys())
