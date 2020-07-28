"""Step implementations for reports."""

import json

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


@then("the client receives the pdf")
def check_pdf(context):
    """Check the pdf."""
    assert_equal("application/pdf", context.response.headers["Content-Type"])
