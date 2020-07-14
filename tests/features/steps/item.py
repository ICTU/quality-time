"""Generic step implementations for reports, subjects, metrics, and sources."""

from asserts import assert_equal, assert_false, assert_not_equal, assert_true
from behave import given, when, then


@given("an existing {item}")
@when("the client creates a {item}")
def add_item(context, item):
    """Add an item."""
    api = f"{item}/new"
    container = dict(source="metric", metric="subject", subject="report").get(item)
    if container:
        api += f"/{context.uuid[container]}"
    context.uuid[item] = context.post(api)[f"new_{item}_uuid"]


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


@when('the client changes the {item} {attribute} to "{value}"')
def change_item_attribute(context, item, attribute, value):
    """Change the item attribute to value."""
    context.post(f"{item}/{context.uuid[item]}/attribute/{attribute}", json={attribute: value})


@then('the {item} {attribute} is "{value}"')
def check_item_attribute(context, item, attribute, value):
    """Check that the item attribute equals value."""
    reports = context.get("reports")
    item_instance = [report for report in reports["reports"] if report["report_uuid"] == context.uuid["report"]][0]
    if item != "report":
        item_instance = item_instance["subjects"][context.uuid["subject"]]
        if item != "subject":
            item_instance = item_instance["metrics"][context.uuid["metric"]]
            if item != "metric":
                item_instance = item_instance["sources"][context.uuid["source"]]
    assert_equal(value, item_instance[attribute])


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


@then("the {container} contains the {item}")
def check_container_contains_item(context, container, item):
    """Check that the container contains the item."""
    reports = context.get("reports")
    container_instance = [report for report in reports["reports"] if report["report_uuid"] == context.uuid["report"]][0]
    if container != "report":
        container_instance = container_instance["subjects"][context.uuid["subject"]]
        if container != "subject":
            container_instance = container_instance["metrics"][context.uuid["metric"]]
    assert_true(context.uuid[item] in container_instance[f"{item}s"])
