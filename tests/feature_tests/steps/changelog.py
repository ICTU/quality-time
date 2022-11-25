"""Step implementations for changelogs."""

from asserts import assert_equal
from behave import then  # pylint: disable=no-name-in-module


@then("the {item} changelog reads")
@then("the changelog reads")
def check_changelog(context, item=None):
    """Check that the changelog contains the text."""
    item_path = f"{item}/{context.uuid[item]}/" if item else ""
    response = context.get(f"changelog/{item_path}10")
    for index, line in enumerate(context.text.split("\n")):
        assert_equal(line, response["changelog"][index]["delta"])
