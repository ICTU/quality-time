"""Step implementations for reports."""

import json
import time
from datetime import datetime, timezone

from asserts import assert_equal
from behave import then, when


@when("the client downloads the report as pdf")
def download_report_as_pdf(context):
    """Download the report as pdf."""
    context.get(f"report/{context.uuid['report']}/pdf")


@when("the client imports a report")
def import_report(context):
    """Import a JSON report."""
    response = context.post("report/import", json=json.loads(context.text))
    context.uuid["report"] = response["new_report_uuid"]


@when("the client enters a report date that's too old")
def time_travel_long_ago(context):
    context.report_date = "2020-08-31T23:00:00.000Z"


@when("the client enters a future report date")
def time_travel_future(context):
    context.report_date = "3000-01-01T10:00:00.000Z"


@when("the client enters a report date that's not too old")
def time_travel(context):
    time.sleep(1)  # Make sure the previously created report is older than the report date
    context.report_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()[: -len("+00:00")] + "Z"
    time.sleep(1)  # Make sure report date is in the past


@then("the client receives the pdf")
def check_pdf(context):
    """Check the pdf."""
    assert_equal("application/pdf", context.response.headers["Content-Type"])
