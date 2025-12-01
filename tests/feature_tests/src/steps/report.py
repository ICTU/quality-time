"""Step implementations for reports."""

import json
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from urllib import parse

from asserts import assert_equal, assert_not_in
from behave import then, when
from dateutil.tz import tzutc

from item import get_item

if TYPE_CHECKING:
    from behave.runner import Context


@when("the client gets the metric status summary")
def get_report_metric_status_summary(context: Context) -> None:
    """Get the report metric status summary."""
    report_uuid = context.uuid["report"]
    with context.external_api():
        context.get(f"report/{report_uuid}/metric_status_summary")


@then("the report metric status summary is returned")
def check_report_metric_status_summary(context: Context) -> None:
    """Check the report metric status summary."""
    summary = context.response.json()
    for color in ("blue", "green", "grey", "red", "white", "yellow"):
        assert_equal(0, summary[color])


@when("the client downloads the report as PDF")
@when("the client downloads the reports overview as PDF")
def download_report_as_pdf(context: Context) -> None:
    """Download the report as PDF."""
    path = "reports_overview" if "overview" in context.step.name else f"report/{context.uuid['report']}"
    context.get(path + "/pdf")


@when("the client downloads the report as JSON")
@when("the client downloads the report {report_uuid} as json")
def download_report_as_json(context: Context, report_uuid: str | None = None) -> None:
    """Download the report as JSON."""
    if report_uuid is None:
        report_uuid = context.uuid["report"]
    with context.external_api():
        report = context.get(f"report/{report_uuid}/json")
    context.exported_report = report


@when("the client downloads the report as JSON with his own public key")
def download_report_as_json_with_key(context: Context) -> None:
    """Download the report as JSON with public key."""
    public_key = parse.quote_plus(context.public_key)
    with context.external_api():
        context.get(f"report/{context.uuid['report']}/json?public_key={public_key}")


@when("the client re-imports a report")
def re_import_report(context: Context) -> None:
    """Import a JSON report."""
    with context.external_api():
        response = context.post("report/import", json=context.exported_report)
    context.uuid["report"] = response["new_report_uuid"]


@when("the client imports a report")
def import_report(context: Context) -> None:
    """Import a JSON report."""
    with context.external_api():
        response = context.post("report/import", json=json.loads(context.text))
    if "new_report_uuid" in response:
        context.uuid["report"] = response["new_report_uuid"]


@when("the client enters a report date that's too old")
def time_travel_long_ago(context: Context) -> None:
    """Set a time before the first report existed."""
    context.report_date = "2020-08-31T23:00:00.000Z"


@when("the client enters a future report date")
def time_travel_future(context: Context) -> None:
    """Set a time in the future."""
    context.report_date = "3000-01-01T10:00:00.000Z"


@when("the client resets the report date")
def reset_report_date(context: Context) -> None:
    """Reset the report date."""
    context.report_date = None


@when("the client enters a report date that's not too old")
def time_travel(context: Context) -> None:
    """Set a time in the past, but after the report was created."""
    time.sleep(1)  # Make sure the previously created report is older than the report date
    context.report_date = datetime.now(tz=tzutc()).replace(microsecond=0).isoformat()[: -len("+00:00")] + "Z"
    time.sleep(1)  # Make sure report date is in the past


@then("the client receives the PDF")
def check_pdf(context: Context) -> None:
    """Check the PDF."""
    assert_equal("application/pdf", context.response.headers["Content-Type"])
    assert_equal(b"%PDF", context.response.content[:4])


@then("the client receives the JSON")
def check_json(context: Context) -> None:
    """Check the JSON."""
    assert_equal(200, context.response.status_code)
    assert_equal("application/json", context.response.headers["Content-Type"])
    assert_not_in("secret", context.response.text)


@then("the client receives no JSON")
def check_no_json(context: Context) -> None:
    """Check the JSON."""
    assert_equal(404, context.response.status_code)


@when("the client gets a non-existing report")
def get_non_existing_report(context: Context) -> None:
    """Get a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.get(f"report/{report_uuid}")


@when("the client copies a non-existing report")
def copy_non_existing_report(context: Context) -> None:
    """Copy a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.post(f"report/{report_uuid}/copy")


@when("the client deletes a non-existing report")
def delete_non_existing_report(context: Context) -> None:
    """Delete a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.delete(f"report/{report_uuid}")


@when('the client changes a non-existing report title to "New title"')
def change_title_of_non_existing_report(context: Context) -> None:
    """Change the title of a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.post(f"report/{report_uuid}/attribute/title", json={"title": "New title"})


@then("the import failed")
def import_failed(context: Context) -> None:
    """Check the JSON."""
    assert_equal(400, context.response.status_code)
    assert_equal("application/json", context.response.headers["Content-Type"])


@then('the report has "{expected_number}" measurements')
def get_measurements(context: Context, expected_number: str) -> None:
    """Get the recent measurements of a report."""
    now = datetime.now(tz=tzutc()).replace(microsecond=0)
    context.report_date = (now + timedelta(days=10)).isoformat()
    context.min_report_date = (now - timedelta(days=10)).isoformat()
    response = context.get("measurements")
    report_measurements = [m for m in response["measurements"] if m["report_uuid"] == context.uuid["report"]]
    assert_equal(int(expected_number), len(report_measurements))


@when('the client changes a non-existing report tracker_type to "jira"')
def change_non_existing_report_tracker_type(context: Context) -> None:
    """Change the issue tracker type of a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.post(f"report/{report_uuid}/issue_tracker/type", json={"type": "jira"})


@when("the client retrieves a non-existing report's issue tracker options")
def get_non_existing_report_tracker_options(context: Context) -> None:
    """Get the issue tracker options of a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.get(f"report/{report_uuid}/issue_tracker/options")


@when("the client retrieves a non-existing report's issue tracker suggestions")
def get_non_existing_report_tracker_suggestions(context: Context) -> None:
    """Get the issue tracker suggestions of a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.get(f"report/{report_uuid}/issue_tracker/suggestions/query")


@when("the client sets the {status} desired response time to {time}")
def set_technical_debt_desired_response_time(context: Context, status: str, time: str) -> None:
    """Set the technical debt desired response time of the specified status."""
    desired_response_times = get_item(context, "report").get("desired_response_times", {})
    desired_response_times[status] = None if time == "empty" else int(time)
    report_uuid = context.uuid["report"]
    context.post(
        f"report/{report_uuid}/attribute/desired_response_times",
        {"desired_response_times": desired_response_times},
    )


@when('the client removes the tag "{tag}" from the report')
def remove_tag(context: Context, tag: str) -> None:
    """Remove the tag from all metrics in the report."""
    report_uuid = context.uuid["report"]
    context.delete(f"report/{report_uuid}/tag/{tag}")


@when('the client renames the tag "{tag}" to "{new_tag}"')
def rename_tag(context: Context, tag: str, new_tag: str) -> None:
    """Rename a tag for all metric in the report."""
    report_uuid = context.uuid["report"]
    context.post(f"report/{report_uuid}/tag/{tag}", {"tag": new_tag})
