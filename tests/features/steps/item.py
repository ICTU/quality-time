"""Generic step implementations for reports, subjects, metrics, and sources."""

from asserts import assert_equal, assert_false, assert_not_equal, assert_true
from behave import given, when, then


@given("an existing {item}")
@given('an existing {item} with {attribute} "{value}"')
@given('an existing {item} with {attribute} "{value}" and parameter {parameter} "{parameter_value}"')
@when("the client creates a {item}")
@when("the client tries to create a {item}")
def add_item(context, item, attribute=None, value=None, parameter=None, parameter_value=None):
    """Add an item with and optionally set attribute to value."""
    api = f"{item}/new"
    container = dict(source="metric", metric="subject", subject="report").get(item)
    if container:
        api += f"/{context.uuid[container]}"
    if "tries to" in context.step.name:
        context.response = context.post(api)
        return
    context.uuid[item] = context.post(api)[f"new_{item}_uuid"]
    if attribute and value:
        context.execute_steps(f'when the client changes the {item} {attribute} to "{value}"')
    if parameter and parameter_value:
        context.execute_steps(f'when the client changes the source parameter {parameter} to "{parameter_value}"')


@when("the client copies the {item}")
def copy_item(context, item):
    """Copy the item."""
    api = f"{item}/{context.uuid[item]}/copy"
    container = dict(source="metric", metric="subject", subject="report").get(item)
    if container:
        api += f"/{context.uuid[container]}"
    context.uuid[item] = context.post(api)[f"new_{item}_uuid"]


@when("the client moves the {item} to the {container}")
def move_item(context, item, container):
    """Move the item."""
    context.post(f"{item}/{context.uuid[item]}/move/{context.uuid[container]}")


@when("the client deletes the {item}")
def delete_subject(context, item):
    """Delete the item."""
    context.delete(f"{item}/{context.uuid[item]}")


@when('the client changes the source parameter {parameter} to "{value}"')
@when('the client changes the source parameter {parameter} to "{value}" with scope "{scope}"')
def change_source_parameter(context, parameter, value, scope="source"):
    """Change the source parameter to value."""
    context.post(f"source/{context.uuid['source']}/parameter/{parameter}", json={parameter: value, "edit_scope": scope})


@when('the client changes the {item} {attribute} to "{value}"')
def change_item_attribute(context, item, attribute, value):
    """Change the item attribute to value."""
    item_fragment = "reports" if item == "reports" else f"{item}/{context.uuid[item]}"
    if attribute == "tags":
        value = value.split(", ")
    else:
        value = dict(true=True, false=False).get(value.lower(), value)
    context.post(f"{item_fragment}/attribute/{attribute}", json={attribute: value})


def get_item(context, item):
    """Return the item instance of type item."""
    item_instance = context.get("reports")
    if item != "reports":
        item_instance = [
            report for report in item_instance["reports"] if report["report_uuid"] == context.uuid["report"]][0]
        if item != "report":
            item_instance = item_instance["subjects"][context.uuid["subject"]]
            if item != "subject":
                item_instance = item_instance["metrics"][context.uuid["metric"]]
                if item != "metric":
                    item_instance = item_instance["sources"][context.uuid["source"]]
    return item_instance


@then('the source parameter {parameter} is "{value}"')
def check_source_parameter(context, parameter, value):
    """Check that the source parameter equals value."""
    assert_equal(value, get_item(context, "source")["parameters"][parameter])


@then('''the parameter {parameter} of the {container}'s sources is "{value}"''')
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


@then('''the parameter {parameter} of all sources is "{value}"''')
def check_all_sources_parameter(context, parameter, value):
    """Check that all sources have a parameter with the specified value."""
    for report in context.get("reports")["reports"]:
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                for source in metric["sources"].values():
                    assert_equal(value, source["parameters"][parameter])


@then('the {item} {attribute} is "{value}"')
def check_item_attribute(context, item, attribute, value):
    """Check that the item attribute equals value."""
    assert_equal(value, get_item(context, item)[attribute])


@then("the {item} does not exist")
def check_item_does_not_exist(context, item):
    """Check that the item does not exist."""
    uuids = []
    reports = context.get("reports")
    for report in reports["reports"]:
        uuids.append(report["report_uuid"])
        uuids.extend(report["subjects"].keys())
        for subject in report["subjects"].values():
            uuids.extend(subject["metrics"].keys())
            for metric in subject["metrics"].values():
                uuids.extend(metric["sources"].keys())
    assert_false(context.uuid[item] in uuids)


def get_container(context, container):
    """Return the container."""
    reports = context.get("reports")
    container_instance = [report for report in reports["reports"] if report["report_uuid"] == context.uuid["report"]][0]
    if container != "report":
        container_instance = container_instance["subjects"][context.uuid["subject"]]
        if container != "subject":
            container_instance = container_instance["metrics"][context.uuid["metric"]]
    return container_instance


@then("the {container} contains the {item}")
def check_container_contains_item(context, container, item):
    """Check that the container contains the item."""
    assert_true(context.uuid[item] in get_container(context, container)[f"{item}s"])


@then('''the {container}'s {position} {item} has {attribute} "{value}"''')
def check_item_order(context, container, position, item, attribute, value):
    """Check that the container item at position has an attribute with the specified value."""
    index = dict(first=0, last=-1)[position]
    assert_equal(value, list(get_container(context, container)[f"{item}s"].values())[index][attribute])
