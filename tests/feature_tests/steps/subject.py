from asserts import assert_equal
from behave import then


@then('the subject {has_or_had} "{expected_number}" measurements')
def get_measurements(context, has_or_had, expected_number):
    """Get the recent measurements of a subject."""
    if has_or_had == "had":
        context.report_date = "2020-11-17T10:00:00Z"
        min_report_date_parameter = "?min_report_date=2020-11-16T00:00:00Z"
    else:
        min_report_date_parameter = ""

    response = context.get(f"subject/{context.uuid['subject']}/measurements{min_report_date_parameter}")
    assert_equal(int(expected_number), len(response["measurements"]))
