"""Generic step implementations for reports, subjects, metrics, and sources."""

import json
from typing import Any, cast

from asserts import assert_equal, assert_false, assert_true
from behave import given, then, when
from behave.runner import Context


@given("an existing {item}")
@given('an existing {item} with {attribute} "{value}"')
@given('an existing {item} with {attribute} "{value}" and parameter {parameter} "{parameter_value}"')
@when("the client creates a {item}")
@when('the client creates a {item} with {attribute} "{value}"')
@when("the client tries to create a {item}")
def add_item(  # noqa: PLR0913
    context: Context,
    item: str,
    attribute: str | None = None,
    value: str | None = None,
    parameter: str | None = None,
    parameter_value: str | None = None,
) -> None:
    """Add an item with and optionally set attribute to value."""
    api = f"{item}/new"
    container = {"source": "metric", "metric": "subject", "subject": "report"}.get(item)
    if container:
        api += f"/{context.uuid[container]}"
    if attribute == "type":
        item_type = value
        attribute = value = None
    else:
        item_type = {"source": "axe_core", "metric": "violations", "subject": "software"}.get(item)
    if "tries to" in context.step.name:
        context.post(api, {"type": item_type})
        return
    context.uuid[item] = context.post(api, {"type": item_type})[f"new_{item}_uuid"]
    if attribute and value:
        context.execute_steps(f'when the client changes the {item} {attribute} to "{value}"')
    if parameter and parameter_value:
        context.execute_steps(f'when the client sets the source parameter {parameter} to "{parameter_value}"')


@when("the client copies the {item}")
def copy_item(context: Context, item: str) -> None:
    """Copy the item."""
    api = f"{item}/{context.uuid[item]}/copy"
    container = {"source": "metric", "metric": "subject", "subject": "report"}.get(item)
    if container:
        api += f"/{context.uuid[container]}"
    context.uuid[item] = context.post(api)[f"new_{item}_uuid"]


@when("the client moves the {item} to the {container}")
def move_item(context: Context, item: str, container: str) -> None:
    """Move the item."""
    context.post(f"{item}/{context.uuid[item]}/move/{context.uuid[container]}")


@when("the client deletes the {item}")
def delete_item(context: Context, item: str) -> None:
    """Delete the item."""
    if item == "notification_destination":
        context.delete(f"report/{context.uuid['report']}/{item}/{context.uuid[item]}")
    else:
        context.delete(f"{item}/{context.uuid[item]}")


@when('the client changes the {item} {attribute} to "{value_str}"')
def change_item_attribute(context: Context, item: str, attribute: str, value_str: str) -> None:
    """Change the item attribute to value."""
    value: str | list[str] | bool | None
    item_fragment = "reports_overview" if item == "reports_overview" else f"{item}/{context.uuid[item]}"
    if attribute in ("tags", "issue_ids"):  # convert comma separated values to lists
        value = value_str.split(", ")
    elif attribute == "permissions":
        if value_str == "None":
            value_str = "{}"
        value = json.loads(value_str)
    else:
        value = {"true": True, "false": False, "none": None}.get(value_str.lower(), value_str)
    if item == "notification_destination":
        context.post(
            f"report/{context.uuid['report']}/{item_fragment}/attributes",
            {attribute: value},
        )
    else:
        if item == "report" and attribute.startswith("tracker"):
            attribute = attribute.split("_", 1)[1]
            attribute_fragment = "issue_tracker"
        else:
            attribute_fragment = "attribute"
        context.post(f"{item_fragment}/{attribute_fragment}/{attribute}", json={attribute: value})


def get_item(context: Context, item: str) -> dict:
    """Return the item instance of type item."""
    item_instance = (
        context.get("reports_overview")
        if item == "reports_overview"
        else context.get(f"report/{context.uuid['report']}")
    )
    if item != "reports_overview":
        item_instance = next(  # pragma: no feature-test-cover
            report for report in item_instance["reports"] if report["report_uuid"] == context.uuid["report"]
        )
        if item == "notification_destination":
            return cast(dict, item_instance["notification_destinations"][context.uuid["notification_destination"]])
        if item != "report":
            item_instance = item_instance["subjects"][context.uuid["subject"]]
            if item != "subject":
                item_instance = item_instance["metrics"][context.uuid["metric"]]
                if item != "metric":
                    item_instance = item_instance["sources"][context.uuid["source"]]
    return cast(dict, item_instance)


@then('the {item} {attribute} is "{value}"')
def check_item_attribute(context: Context, item: str, attribute: str, value: str) -> None:
    """Check that the item attribute equals the expected value."""
    if item == "reports_overview" and attribute == "permissions":  # parse JSON data
        expected_value = {} if value == "None" else json.loads(value)
    else:
        expected_value = None if value == "None" else value

    keys = attribute.split(".")
    actual_value: Any = get_item(context, item)
    for key in keys:
        actual_value = actual_value[key]
    if attribute in ("tags", "issue_ids"):  # convert lists to comma separated values
        actual_value = ", ".join(actual_value)

    assert_equal(expected_value, actual_value)


@then("the {item} does not exist")
def check_item_does_not_exist(context: Context, item: str) -> None:
    """Check that the item does not exist."""
    uuids = []
    reports = context.get(f"report/{context.uuid[item]}") if item == "report" else context.get("report/")
    for report in reports["reports"]:
        uuids.append(report["report_uuid"])
        uuids.extend(report["subjects"].keys())
        for subject in report["subjects"].values():
            uuids.extend(subject["metrics"].keys())
            for metric in subject["metrics"].values():
                uuids.extend(metric["sources"].keys())
    assert_false(context.uuid[item] in uuids)


def get_container(context: Context, container: str) -> dict:
    """Return the container."""
    reports = context.get("report/")
    container_instance = next(  # pragma: no feature-test-cover
        report for report in reports["reports"] if report["report_uuid"] == context.uuid["report"]
    )
    if container != "report":
        container_instance = container_instance["subjects"][context.uuid["subject"]]
        if container != "subject":
            container_instance = container_instance["metrics"][context.uuid["metric"]]
    return cast(dict, container_instance)


@then("the {container} contains the {item}")
def check_container_contains_item(context: Context, container: str, item: str) -> None:
    """Check that the container contains the item."""
    assert_true(context.uuid[item] in get_container(context, container)[f"{item}s"])


@then('''the {container}'s {position} {item} has {attribute} "{value}"''')
def check_item_order(  # noqa: PLR0913
    context: Context,
    container: str,
    position: str,
    item: str,
    attribute: str,
    value: str,
) -> None:
    """Check that the container item at position has an attribute with the specified value."""
    index = {"first": 0, "last": -1}[position]
    assert_equal(
        value,
        list(get_container(context, container)[f"{item}s"].values())[index][attribute],
    )


@then("the {container} contains {number} {children}")
def check_nr_children(context: Context, container: str, number: str, children: str) -> None:
    """Check that the container has the expected number of child items."""
    if container == "reports overview":
        reports = context.get("report/")
        assert_equal(number, str(len(reports)))
    else:
        container_instance = get_container(context, container)
        children = children if children.endswith("s") else children + "s"
        assert_equal(number, str(len(container_instance[children])))
