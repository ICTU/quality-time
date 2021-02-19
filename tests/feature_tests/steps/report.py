"""Step implementations for reports."""

import json
import time
import urllib
from datetime import datetime, timezone

from asserts import assert_equal
from behave import then, when


@when("the client downloads the report as pdf")
def download_report_as_pdf(context):
    """Download the report as pdf."""
    context.get(f"report/{context.uuid['report']}/pdf")


@when("the client downloads the report as json")
def download_report_as_json(context):
    """Download the report as json."""
    context.get(f"report/{context.uuid['report']}/json")


@when("the client downloads the report as json with his own public key")
def download_report_as_json_with_key(context):
    """Download the report as json with public key."""
    public_key = urllib.parse.quote_plus(context.public_key)
    context.get(f"report/{context.uuid['report']}/json?public_key={public_key}")


@when("the client downloads the report with a faulty key")
def download_report_with_faulty_key(context):
    """Download the report with a faulty key."""
    faulty_public_key = urllib.parse.quote_plus(context.faulty_public_key)
    context.get(f"report/{context.uuid['report']}/json?public_key={faulty_public_key}")


@when("the client imports a report")
def import_report(context):
    """Import a JSON report."""
    response = context.post("report/import", json=json.loads(context.text))
    context.uuid["report"] = response["new_report_uuid"]


@when("the client enters a report date that's too old")
def time_travel_long_ago(context):
    """Set a time before the first report existed."""
    context.report_date = "2020-08-31T23:00:00.000Z"


@when("the client enters a future report date")
def time_travel_future(context):
    """Set a time in the future."""
    context.report_date = "3000-01-01T10:00:00.000Z"


@when("the client enters a report date that's not too old")
def time_travel(context):
    """Set a time in the past, but after the report was created."""
    time.sleep(1)  # Make sure the previously created report is older than the report date
    context.report_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()[: -len("+00:00")] + "Z"
    time.sleep(1)  # Make sure report date is in the past


@then("the client receives the pdf")
def check_pdf(context):
    """Check the pdf."""
    assert_equal("application/pdf", context.response.headers["Content-Type"])


@then("the client receives the json")
def check_json(context):
    """Check the json."""
    assert_equal(200, context.response.status_code)
    assert_equal("application/json", context.response.headers["Content-Type"])


@then("the client receives a json error")
def check_json_error(context):
    """Check the json error."""
    assert_equal(400, context.response.status_code)
    assert_equal("application/json", context.response.headers["Content-Type"])


@when("the client gets a non-existing report")
def get_non_existing_report(context):
    """Get a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.get(f"report/{report_uuid}")
