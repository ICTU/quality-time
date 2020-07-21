"""Step implementations for measurement."""

from asserts import assert_equal, assert_true


@when("the collector gets the metrics to measure")
def get_metrics(context):
    """Get the metrics to measure from the server."""
    context.metrics = context.get("metrics")


@when('the collector measures "{number}"')
def measure(context, number):
    """Post the measurement."""
    entities = [
        dict(key=row["key"], value=row["value"], notes=row["notes"]) for row in context.table] if context.table else []
    context.post(
        "measurements",
        json=dict(
            metric_uuid=context.uuid["metric"],
            sources=[
                dict(source_uuid=context.uuid["source"], parse_error=None, connection_error=None, value=number,
                     total="100", entities=entities)]))


@when('the client sets the {attribute} of entity {key} to "{value}"')
def set_entity_attribute(context, attribute, key, value):
    """Set the entity attribute to the specified value."""
    context.post(
        f"measurement/{context.uuid['metric']}/source/{context.uuid['source']}/entity/{key}/{attribute}",
        json={attribute: value})


@then("the metric needs to be measured")
def check_metrics(context):
    """Check that the metric needs to be measured."""
    assert_true(context.uuid["metric"] in context.metrics.keys())


@then("the metric has one measurement")
@then("the metric has {count} measurements")
def check_nr_of_measurements(context, count="one"):
    """Check that the metric has the expected number of measurements."""
    expected_number = dict(one=1, two=2).get(count, count)
    assert_equal(int(expected_number), len(context.get(f"measurements/{context.uuid['metric']}")["measurements"]))
