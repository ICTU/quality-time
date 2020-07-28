"""Step implementations for measurement."""

import time

from asserts import assert_equal, assert_true
from behave import then, when
from sseclient import SSEClient


@when("the collector gets the metrics to measure")
def get_metrics(context):
    """Get the metrics to measure from the server."""
    context.get("metrics")


@when('the collector measures "{number}"')
@when('the collector measures "{number}" with total "{total}"')
def measure(context, number, total="100"):
    """Post the measurement."""
    entities = []
    if context.table:
        for row in context.table:
            entity = dict((heading, row[heading]) for heading in context.table.headings)
            entities.append(entity)
    context.post(
        "measurements",
        json=dict(
            metric_uuid=context.uuid["metric"],
            sources=[
                dict(source_uuid=context.uuid["source"], parse_error=None, connection_error=None, value=number,
                     total=total, entities=entities)]))


@when("the collector encounters a parse error")
def parse_error(context):
    """Post the parse error."""
    context.post(
        "measurements",
        json=dict(
            metric_uuid=context.uuid["metric"],
            sources=[
                dict(source_uuid=context.uuid["source"], parse_error="Parse error", connection_error=None, value=None,
                     total=None, entities=[])]))


@when('the client sets the {attribute} of entity {key} to "{value}"')
def set_entity_attribute(context, attribute, key, value):
    """Set the entity attribute to the specified value."""
    context.post(
        f"measurement/{context.uuid['metric']}/source/{context.uuid['source']}/entity/{key}/{attribute}",
        json={attribute: value})


@when("the client connects to the number of measurements {stream}")
def connect_to_nr_of_measurements_stream(context, stream):
    """Get the number of measurements server-sent-events."""
    context.sse_messages = []
    for message in SSEClient(f"{context.base_api_url}/nr_measurements"):  # pragma: no cover-behave
        context.sse_messages.append(message)
        if stream == "stream":
            break
        context.execute_steps('when the collector measures "42"')
        stream = "stream"


@then("the server skips the next update because nothing changed")
def skip_update(context):
    """Sleep > 10 seconds to give server a chance to skip the next update."""
    time.sleep(11)


@then("the metric needs to be measured")
def check_metrics(context):
    """Check that the metric needs to be measured."""
    assert_true(context.uuid["metric"] in context.response.json().keys())


@then("the metric has one measurement")
@then("the metric has {count} measurements")
def check_nr_of_measurements(context, count="one"):
    """Check that the metric has the expected number of measurements."""
    expected_number = dict(no=0, one=1, two=2).get(count, count)
    assert_equal(int(expected_number), len(context.get(f"measurements/{context.uuid['metric']}")["measurements"]))


@then("the server sends the number of measurements {message_type} message")
def check_nr_of_measurements_stream(context, message_type):
    """Check the server-sent events."""
    if message_type == "init":
        assert_equal("0", context.sse_messages[0].id)
    else:
        assert_equal(int(context.sse_messages[-2].data) + 1, int(context.sse_messages[-1].data))
