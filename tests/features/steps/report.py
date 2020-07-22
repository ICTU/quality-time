"""Step implementations for reports."""

from asserts import assert_equal
from behave import when


@when("the client downloads the report as pdf")
def download_report_as_pdf(context):
    """Download the report as pdf."""
    context.response = context.get(f"report/{context.uuid['report']}/pdf")


@then("the client receives the pdf")
def check_pdf(context):
    """Check the pdf."""
    assert_equal("application/pdf", context.response.headers["Content-Type"])
