"""Step implementations for measurement."""

import time
from datetime import UTC, datetime, timedelta

from asserts import assert_equal, assert_in
from behave import given, then, when
from behave.runner import Context
from sseclient import SSEClient


def create_measurement(  # noqa: PLR0913
    context: Context,
    status: str | None = None,
    value: str | None = None,
    total: str | None = None,
    issue_id: str | None = None,
    issue_status_name: str | None = None,
    parse_error: str | None = None,
) -> dict:
    """Create a measurement."""
    entities = []
    if context.table:
        for row in context.table:
            entity = {heading: row[heading] for heading in context.table.headings}
            entities.append(entity)
    measurement_datetime = datetime.now(tz=UTC)
    measurement_timestamp = measurement_datetime.replace(microsecond=0).isoformat()
    if issue_id:
        status_category = "done" if issue_status_name == "Completed" else "todo"
        issues = [{"issue_id": issue_id, "name": issue_status_name, "status_category": status_category}]
    else:
        issues = []
    return {
        "metric_uuid": context.uuid["metric"],
        "report_uuid": context.uuid["report"],
        "has_error": False,
        "sources": [
            {
                "source_uuid": context.uuid["source"],
                "parse_error": parse_error,
                "connection_error": None,
                "value": value,
                "total": total,
                "entities": entities,
            },
        ],
        "count": {"status": status, "value": value},
        "percentage": {"status": status, "value": value},
        "version_number": {"status": status, "value": value},
        "issue_status": issues,
        "start": measurement_timestamp,
        "end": measurement_timestamp,
    }


@given('the collector has measured "{number}"')
@when('the collector measures "{number}"')
@when('the collector measures "{number}" with status "{status}"')
@when('the collector measures "{number}" with total "{total}"')
def measure(context: Context, number: str, status: str = "target_met", total: str = "100") -> None:
    """Enter a measurement with the given value into the measurement collection in the database."""
    measurement = create_measurement(context, status, number, total)
    context.database.measurements.insert_one(measurement)


@when("the collector measures issue '{issue_id}' status '{name}'")
@when("the collector measures '{number}' with issue '{issue_id}' status '{name}'")
def measure_issue_status(context: Context, issue_id: str, name: str, number: str = "10") -> None:
    """Enter a measurement with the issue status into the measurement collection in the database."""
    measurement = create_measurement(context, "target_met", number, "100", issue_id, name)
    context.database.measurements.insert_one(measurement)


@when("the collector encounters a parse error")
def parse_error(context: Context) -> None:
    """Enter a measurement with a parse error into the measurement collection in the database."""
    measurement = create_measurement(context, parse_error="Parse error")
    context.database.measurements.insert_one(measurement)


@when('the client sets the {attribute} of entity {key} to "{value}"')
def set_entity_attribute(context: Context, attribute: str, key: str, value: str) -> None:
    """Set the entity attribute to the specified value."""
    context.post(
        f"measurement/{context.uuid['metric']}/source/{context.uuid['source']}/entity/{key}/{attribute}",
        json={attribute: value},
    )


@when("the client connects to the number of measurements {stream}")
def connect_to_nr_of_measurements_stream(context: Context, stream: str) -> None:
    """Get the number of measurements server-sent-events."""
    context.sse_messages = []
    for message in SSEClient(f"{context.base_api_url}/nr_measurements"):  # pragma: no feature-test-cover
        context.sse_messages.append(message)
        if stream == "stream":
            break
        context.execute_steps('when the collector measures "42"')
        stream = "stream"


@then("the server skips the next update because nothing changed")
def skip_update(_context: Context) -> None:
    """Sleep > 10 seconds to give server a chance to skip the next update."""
    time.sleep(10.1)


@then("the metric {has_or_had} one measurement")
@then("the metric {has_or_had} {count} measurements")
def check_nr_of_measurements(context: Context, has_or_had: str, count: str = "one") -> None:
    """Check that the metric has the expected number of measurements."""
    if has_or_had == "had":
        context.report_date = "2020-11-17T10:00:00Z"
    expected_number = {"no": 0, "one": 1, "two": 2}.get(count, count)
    assert_equal(
        int(expected_number),
        len(context.get(f"measurements/{context.uuid['metric']}")["measurements"]),
    )


@then("the server sends the number of measurements {message_type} message")
def check_nr_of_measurements_stream(context: Context, message_type: str) -> None:
    """Check the server-sent events."""
    if message_type == "init":
        assert_equal("0", context.sse_messages[0].id)
    else:
        assert_equal(int(context.sse_messages[-2].data) + 1, int(context.sse_messages[-1].data))


@when("the client gets {the_current_or_past} reports overview measurements")
def get_reports_overview_measurements(context: Context, the_current_or_past: str) -> None:
    """Get the reports overview measurements."""
    if the_current_or_past == "past":
        now = datetime.now(tz=UTC)
        just_now = now - timedelta(seconds=1)
        last_week = now - timedelta(days=7)
        context.report_date = just_now.isoformat()
        context.min_report_date = last_week.isoformat()
    context.get("measurements")


@then("the server returns the reports overview measurements")
def check_reports_overview_measurements(context: Context) -> None:
    """Check that the response contains the measurements."""
    assert_in("measurements", context.response.json())
