from asserts import assert_equal
from behave import then


@then('the subject {has_or_had} "{expected_number}" measurements')
def get_measurements(context, has_or_had, expected_number):
    """Get the recent measurements of a subject."""
    if has_or_had == "had":
        context.report_date = "2020-11-17T10:00:00Z"

    response = context.get(f"subject/{context.uuid['subject']}/measurements")
    assert_equal(int(expected_number), len(response["measurements"]))
