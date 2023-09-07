"""Data model source parameters."""

from typing import Literal, Self

from pydantic import HttpUrl, model_validator

from .meta.parameter import Parameter, ParameterType
from .meta.unit import Unit


class DateParameter(Parameter):
    """Date parameter."""

    type: ParameterType = ParameterType.DATE  # noqa: A003


class StringParameter(Parameter):
    """String parameter."""

    type: ParameterType = ParameterType.STRING  # noqa: A003


class IntegerParameter(Parameter):
    """Integer parameter."""

    type: ParameterType = ParameterType.INTEGER  # noqa: A003
    default_value: str | list[str] = "0"
    min_value: str = "0"

    @model_validator(mode="after")
    def check_unit(self) -> Self:
        """Check that integer-type parameters have a unit."""
        if self.unit is None:
            msg = f"Parameter {self.name} has no unit"  # type: ignore[unreachable]
            raise ValueError(msg)
        return self


class URL(Parameter):
    """URL parameter."""

    name: str = "URL"
    short_name: str = "URL"
    mandatory: bool = True
    validate_on: list[str] = ["username", "password", "private_token"]
    type: ParameterType = ParameterType.URL  # noqa: A003


class LandingURL(StringParameter):
    """URL to a human readable version of a CSV, XML, or JSON report.

    This is a string parameter because Quality-time doesn't validate these URLs.
    """

    short_name: str = "URL"


class SingleChoiceParameter(Parameter):
    """Single choice parameter."""

    type: ParameterType = ParameterType.SINGLE_CHOICE  # noqa: A003


class MultipleChoiceParameter(Parameter):
    """Multiple choice parameter."""

    type: ParameterType = ParameterType.MULTIPLE_CHOICE  # noqa: A003
    default_value: str | list[str] = []


class MultipleChoiceWithAdditionParameter(MultipleChoiceParameter):
    """Multiple choice parameter that allows the user to add additional options."""

    type: ParameterType = ParameterType.MULTIPLE_CHOICE_WITH_ADDITION  # noqa: A003
    placeholder: str = "none"


class Username(StringParameter):
    """User to be used for authentication."""

    name: str = "Username for basic authentication"
    short_name: str = "username"


class Password(Parameter):
    """Password parameter."""

    name: str = "Password for basic authentication"
    short_name: str = "password"
    type: ParameterType = ParameterType.PASSWORD  # noqa: A003


class PrivateToken(Password):
    """Private token for authentication."""

    name: str = "Private token"
    short_name: str = "private token"
    validation_path: str = ""  # URL path to use for the validation of tokens


class Days(IntegerParameter):
    """Number of days parameter."""

    unit: Unit = Unit.DAYS
    min_value: str = "1"


class Severities(MultipleChoiceParameter):
    """Security warning severities."""

    name: str = "Severities"
    placeholder: str = "all severities"
    metrics: list[str] = ["security_warnings"]

    @model_validator(mode="after")
    def set_help(self) -> Self:
        """Add a default help string if a help URL was not provided."""
        if not self.help and not self.help_url:
            self.help = "If provided, only count security warnings with the selected severities."
        return self


class TestResult(MultipleChoiceParameter):
    """Test result parameter."""

    name: str = "Test results"
    help: str = (  # noqa: A003
        "Limit which test results to count. Note: depending on which results are selected, the direction of the "
        "metric may need to be adapted. For example, when counting passed tests, more is better, but when counting "
        "failed tests, fewer is better."
    )
    placeholder: str = "all test results"
    metrics: list[str] = ["tests"]


class Upvotes(IntegerParameter):
    """Minimum number of merge request up-votes parameter."""

    name: str = "Minimum number of upvotes"
    short_name: str = "minimum upvotes"
    help: str = "Only count merge requests with fewer than the minimum number of upvotes."  # noqa: A003
    unit: Unit = Unit.UPVOTES
    metrics: list[str] = ["merge_requests"]


class Branch(StringParameter):
    """Branch name parameter."""

    name: str = "Branch"
    default_value: str | list[str] = "master"
    metrics: list[str] = ["source_up_to_dateness"]


class BranchesToIgnore(MultipleChoiceWithAdditionParameter):
    """Branches to ignore parameter."""

    name: str = "Branches to ignore (regular expressions or branch names)"
    short_name: str = "branches to ignore"
    metrics: list[str] = ["unmerged_branches"]


class TargetBranchesToInclude(MultipleChoiceWithAdditionParameter):
    """Target branches to include parameter."""

    name: str = "Target branches to include (regular expressions or branch names)"
    short_name: str = "target branches to include"
    placeholder: str = "all target branches"
    metrics: list[str] = ["merge_requests"]


class MergeRequestState(MultipleChoiceParameter):
    """Merge request states parameter."""

    name: str = "Merge request states"
    short_name: str = "states"
    help: str = "Limit which merge request states to count."  # noqa: A003
    placeholder: str = "all states"
    metrics: list[str] = ["merge_requests"]


class FailureType(MultipleChoiceParameter):
    """Failure type parameter."""

    name: str = "Failure types"
    help: str = "Limit which failure types to count as failed."  # noqa: A003
    placeholder: str = "all failure types"
    metrics: list[str] = ["failed_jobs"]


def access_parameters(
    metrics: list[str],
    include: dict[str, bool] | None = None,
    source_type: str = "",
    source_type_format: Literal["", "CSV", "HTML", "JSON", "XML"] = "",
    kwargs: dict[str, dict[str, str | bool | HttpUrl | list[str]]] | None = None,
) -> dict[str, Parameter]:
    """Create the access parameters, needed to access the source."""
    include = include or {}
    kwargs = kwargs or {}
    parameters: dict[str, Parameter] = {
        "username": Username(metrics=metrics, **kwargs.get("username", {})),
        "password": Password(metrics=metrics, **kwargs.get("password", {})),
    }
    validate_on = ["username", "password"]
    if include.get("private_token", True):
        private_token_kwargs = kwargs.get("private_token", {})
        parameters["private_token"] = PrivateToken(metrics=metrics, **private_token_kwargs)
        validate_on.append("private_token")
    url_kwargs = kwargs.get("url") or {"name": "URL"}
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
