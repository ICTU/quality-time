"""Step implementations for reports."""

import json
import time
import urllib
from datetime import datetime, timezone

from asserts import assert_equal, assert_not_in
from behave import then, when  # pylint: disable=no-name-in-module


@when("the client downloads the report as PDF")
def download_report_as_pdf(context):
    """Download the report as PDF."""
    context.get(f"report/{context.uuid['report']}/pdf")


@when("the client downloads the report as JSON")
@when("the client downloads the report {report_uuid} as json")
def download_report_as_json(context, report_uuid=None):
    """Download the report as JSON."""
    if report_uuid is None:
        report_uuid = context.uuid["report"]
    report = context.get(f"report/{report_uuid}/json")
    context.exported_report = report


@when("the client downloads the report as JSON with his own public key")
def download_report_as_json_with_key(context):
    """Download the report as JSON with public key."""
    public_key = urllib.parse.quote_plus(context.public_key)
    context.get(f"report/{context.uuid['report']}/json?public_key={public_key}")


@when("the client re-imports a report")
def re_import_report(context):
    """Import a JSON report."""
    response = context.post("report/import", json=context.exported_report)
    context.uuid["report"] = response["new_report_uuid"]


@when("the client imports a report")
def import_report(context):
    """Import a JSON report."""
    response = context.post("report/import", json=json.loads(context.text))
    if "new_report_uuid" in response:
        context.uuid["report"] = response["new_report_uuid"]


@when("the client enters a report date that's too old")
def time_travel_long_ago(context):
    """Set a time before the first report existed."""
    context.report_date = "2020-08-31T23:00:00.000Z"


@when("the client enters a future report date")
def time_travel_future(context):
    """Set a time in the future."""
    context.report_date = "3000-01-01T10:00:00.000Z"


@when("the client resets the report date")
def reset_report_date(context):
    """Reset the report date."""
    context.report_date = None


@when("the client enters a report date that's not too old")
def time_travel(context):
    """Set a time in the past, but after the report was created."""
    time.sleep(1)  # Make sure the previously created report is older than the report date
    context.report_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()[: -len("+00:00")] + "Z"
    time.sleep(1)  # Make sure report date is in the past


@then("the client receives the PDF")
def check_pdf(context):
    """Check the PDF."""
    assert_equal("application/pdf", context.response.headers["Content-Type"])


@then("the client receives the JSON")
def check_json(context):
    """Check the JSON."""
    assert_equal(200, context.response.status_code)
    assert_equal("application/json", context.response.headers["Content-Type"])
    assert_not_in("secret", context.response.text)


@then("the client receives no JSON")
def check_no_json(context):
    """Check the JSON."""
    assert_equal(404, context.response.status_code)


@when("the client gets a non-existing report")
def get_non_existing_report(context):
    """Get a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.get(f"report/{report_uuid}")


@then("the import failed")
def import_failed(context):
    """Check the JSON."""
    assert_equal(400, context.response.status_code)
    assert_equal("application/json", context.response.headers["Content-Type"])


@then('the report {has_or_had} "{expected_number}" measurements')
def get_measurements(context, has_or_had, expected_number):
    """Get the recent measurements of a report."""
    if has_or_had == "had":
        context.report_date = "2020-11-17T10:00:00Z"
        context.min_report_date = "2020-11-16T00:00:00Z"

    response = context.get("measurements")
    report_measurements = [m for m in response["measurements"] if m["report_uuid"] == context.uuid["report"]]
    assert_equal(int(expected_number), len(report_measurements))
