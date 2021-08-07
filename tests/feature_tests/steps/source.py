"""Step implementations for sources."""

from asserts import assert_equal, assert_false, assert_not_equal, assert_in
from behave import then, when

from item import get_item


def sanitize_value(value: str):
    """Convert the value if necessary."""
    if value == "None":
        return ""
    if "[" in value:
        # Split the list items and strip the quotes:
        return [item[1:-1] for item in value[1:-1].split(", ")]
    return value


@when('the client sets the source parameter {parameter} to "{value}"')
@when('the client sets the source parameter {parameter} to "{value}" with scope "{scope}"')
def change_source_parameter(context, parameter, value, scope="source"):
    """Change the source parameter to value."""
    context.post(
        f"source/{context.uuid['source']}/parameter/{parameter}",
        json={parameter: sanitize_value(value), "edit_scope": scope},
    )


@then('the source parameter {parameter} equals "{value}"')
def check_source_parameter(context, parameter, value):
    """Check that the source parameter equals value."""
    source = get_item(context, "source")
    assert_equal(sanitize_value(value), source["parameters"][parameter])


@then('the availability status code equals "{status_code}"')
def check_source_parameter_availability_status_code(context, status_code):
    """Check the availability status code."""
    post_response = context.post_response.json()
    if status_code == "None":
        assert_false("availability" in post_response)
    else:
        assert_equal(status_code, str(post_response["availability"][0]["status_code"]))


@then('the availability status reason equals "{message1}"')
@then('the availability status reason equals either "{message1}" or "{message2}"')
def check_source_parameter_availability_reason(context, message1, message2=""):
    """Check the availability message."""
    post_response = context.post_response.json()
    reason = str(post_response["availability"][0]["reason"])
    if message1 and message2:
        assert_in(reason, (message1, message2))
    elif message1:
        assert_equal(message1, reason)


@then('''the parameter {parameter} of the {container}'s sources equals "{value}"''')
def check_sources_parameter(context, parameter, container, value):
    """Check that all sources within the container have a parameter with the specified value."""
    if container == "metric":
        metrics = [get_item(context, "metric")]
    elif container == "subject":
        subject = get_item(context, "subject")
        metrics = subject["metrics"].values()
    else:
        report = get_item(context, "report")
        subjects = report["subjects"].values()
        metrics = [metric for subject in subjects for metric in subject["metrics"].values()]
    for metric in metrics:
        for source in metric["sources"].values():
            assert_equal(value, source["parameters"][parameter])


@then('the parameter {parameter} of all sources does not equal "{value}"')
def check_all_sources_parameter(context, parameter, value):
    """Check that all sources have a parameter with the specified value."""
    for report in context.get("report/")["reports"]:
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                for source in metric["sources"].values():
                    assert_not_equal(value, source["parameters"].get(parameter))


@then('"{path}" is returned as source logo')
def check_source_logo(context, path):
    """Check that the correct source logo is returned."""
    source_type = get_item(context, "source")["type"]
    logo_via_server = context.get(f"logo/{source_type}").content
    logo_on_disk = open(path, "rb").read()
    assert_equal(logo_via_server, logo_on_disk)
