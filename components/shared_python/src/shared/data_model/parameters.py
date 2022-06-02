"""Data model source parameters."""

from typing import Literal, Optional, Union

from pydantic import validator  # pylint: disable=no-name-in-module

from .meta.parameter import Parameter, ParameterType
from .meta.unit import Unit


class DateParameter(Parameter):  # pylint: disable=too-few-public-methods
    """Date parameter."""

    type: ParameterType = ParameterType.DATE


class StringParameter(Parameter):  # pylint: disable=too-few-public-methods
    """String parameter."""

    type: ParameterType = ParameterType.STRING


class IntegerParameter(Parameter):  # pylint: disable=too-few-public-methods
    """Integer parameter."""

    type: ParameterType = ParameterType.INTEGER
    default_value: Union[str, list[str]] = "0"
    min_value: str = "0"

    @validator("unit", always=True)
    def check_unit(cls, unit, values):  # pylint: disable=no-self-argument
        """Check that integer-type parameters have a unit."""
        if unit is None:
            raise ValueError(f"Parameter {values['name']} has no unit")
        return unit


class URL(Parameter):  # pylint: disable=too-few-public-methods
    """URL parameter."""

    name: str = "URL"
    short_name = "URL"
    mandatory = True
    validate_on: list[str] = ["username", "password", "private_token"]
    type = ParameterType.URL


class LandingURL(StringParameter):  # pylint: disable=too-few-public-methods
    """URL to a human readable version of a CSV, XML, or JSON report.

    This is a string parameter because Quality-time doesn't validate these URLs.
    """

    short_name = "URL"


class SingleChoiceParameter(Parameter):  # pylint: disable=too-few-public-methods
    """Single choice parameter."""

    type = ParameterType.SINGLE_CHOICE


class MultipleChoiceParameter(Parameter):  # pylint: disable=too-few-public-methods
    """Multiple choice parameter."""

    type = ParameterType.MULTIPLE_CHOICE
    default_value: Union[str, list[str]] = []


class MultipleChoiceWithAdditionParameter(MultipleChoiceParameter):  # pylint: disable=too-few-public-methods
    """Multiple choice parameter that allows the user to add additional options."""

    type = ParameterType.MULTIPLE_CHOICE_WITH_ADDITION
    placeholder = "none"


class Username(StringParameter):  # pylint: disable=too-few-public-methods
    """User to be used for authentication."""

    name: str = "Username for basic authentication"
    short_name = "username"


class Password(Parameter):  # pylint: disable=too-few-public-methods
    """Password parameter."""

    name: str = "Password for basic authentication"
    short_name = "password"
    type = ParameterType.PASSWORD


class PrivateToken(Password):  # pylint: disable=too-few-public-methods
    """Private token for authentication."""

    name: str = "Private token"
    short_name = "private token"
    validation_path: str = ""  # URL path to use for the validation of tokens


class Days(IntegerParameter):  # pylint: disable=too-few-public-methods
    """Number of days parameter."""

    unit: Unit = Unit.DAYS
    min_value = "1"


class Severities(MultipleChoiceParameter):
    """Security warning severities."""

    name: str = "Severities"
    placeholder = "all severities"
    metrics: list[str] = ["security_warnings"]

    @validator("help_url", always=True)
    def set_help(cls, help_url, values):  # pylint: disable=no-self-argument
        """Add a default help string if a help URL was not provided."""
        if not help_url and not values.get("help"):
            values["help"] = "If provided, only count security warnings with the selected severities."
        return help_url


class TestResult(MultipleChoiceParameter):  # pylint: disable=too-few-public-methods
    """Test result parameter."""

    name: str = "Test results"
    help: Optional[str] = (
        "Limit which test results to count. Note: depending on which results are selected, the direction of the "
        "metric may need to be adapted. For example, when counting passed tests, more is better, but when "
        "counting failed tests, fewer is better."
    )
    placeholder = "all test results"
    metrics: list[str] = ["tests"]


class Upvotes(IntegerParameter):  # pylint: disable=too-few-public-methods
    """Minimum number of merge request up-votes parameter."""

    name: str = "Minimum number of upvotes"
    short_name = "minimum upvotes"
    help: Optional[str] = "Only count merge requests with fewer than the minimum number of upvotes."
    unit: Unit = Unit.UPVOTES
    metrics: list[str] = ["merge_requests"]


class Branch(StringParameter):  # pylint: disable=too-few-public-methods
    """Branch name parameter."""

    name: str = "Branch"
    default_value: Union[str, list[str]] = "master"
    metrics: list[str] = ["source_up_to_dateness"]


class BranchesToIgnore(MultipleChoiceWithAdditionParameter):  # pylint: disable=too-few-public-methods
    """Branches to ignore parameter."""

    name: str = "Branches to ignore (regular expressions or branch names)"
    short_name = "branches to ignore"
    metrics: list[str] = ["unmerged_branches"]


class TargetBranchesToInclude(MultipleChoiceWithAdditionParameter):  # pylint: disable=too-few-public-methods
    """Target branches to include parameter."""

    name: str = "Target branches to include (regular expressions or branch names)"
    short_name = "target branches to include"
    placeholder = "all target branches"
    metrics: list[str] = ["merge_requests"]


class MergeRequestState(MultipleChoiceParameter):  # pylint: disable=too-few-public-methods
    """Merge request states parameter."""

    name: str = "Merge request states"
    short_name = "states"
    help: Optional[str] = "Limit which merge request states to count."
    placeholder = "all states"
    metrics: list[str] = ["merge_requests"]


class FailureType(MultipleChoiceParameter):  # pylint: disable=too-few-public-methods
    """Failure type parameter."""

    name: str = "Failure types"
    help: Optional[str] = "Limit which failure types to count as failed."
    placeholder = "all failure types"
    metrics: list[str] = ["failed_jobs"]


def access_parameters(
    metrics: list[str],
    include: dict[str, bool] = None,
    source_type: str = "",
    source_type_format: Literal["", "CSV", "HTML", "JSON", "XML"] = "",
    kwargs: dict[str, dict[str, Union[str, bool, list[str]]]] = None,
) -> dict[str, Parameter]:
    """Create the access parameters, needed to access the source."""
    include = include or {}
    kwargs = kwargs or {}
    parameters: dict[str, Parameter] = dict(
        username=Username(metrics=metrics, **kwargs.get("username", {})),
        password=Password(metrics=metrics, **kwargs.get("password", {})),
    )
    validate_on = ["username", "password"]
    if include.get("private_token", True):
        parameters["private_token"] = PrivateToken(metrics=metrics, **kwargs.get("private_token", {}))
        validate_on.append("private_token")
    url_kwargs = kwargs.get("url") or dict(name="URL")
    if source_type:
        source_type_article = "an" if source_type.startswith("an ") else "a"
        source_type = source_type[len("an ") :] if source_type.startswith("an ") else source_type
        format_phrase = f" in {source_type_format} format" if source_type_format else ""
        url_kwargs["name"] = (
            f"URL to {source_type_article} {source_type}{format_phrase} or to a zip "
            f"with {source_type}s{format_phrase}"
        )
    url_kwargs.setdefault("metrics", metrics)
    parameters["url"] = URL(validate_on=validate_on, **url_kwargs)
    if include.get("landing_url", source_type_format != "HTML"):
        landing_url_name = f"URL to {source_type_article} {source_type} in a human readable format"
        landing_url_help = (
            "If provided, users clicking the source URL will visit this URL instead of the "
            f"{source_type} in {source_type_format} format."
        )
        parameters["landing_url"] = LandingURL(metrics=metrics, name=landing_url_name, help=landing_url_help)
    return parameters
