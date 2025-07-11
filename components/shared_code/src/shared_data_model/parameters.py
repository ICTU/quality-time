"""Data model source parameters."""

from typing import Literal, Self

from pydantic import HttpUrl, model_validator

from .meta.parameter import Parameter, ParameterType
from .meta.unit import Unit


class DateParameter(Parameter):
    """Date parameter."""

    type: ParameterType = ParameterType.DATE


class StringParameter(Parameter):
    """String parameter."""

    type: ParameterType = ParameterType.STRING


class IntegerParameter(Parameter):
    """Integer parameter."""

    type: ParameterType = ParameterType.INTEGER
    default_value: str | list[str] = "0"
    min_value: str = "0"

    @model_validator(mode="after")
    def check_unit(self) -> Self:
        """Check that integer-type parameters have a unit."""
        if self.unit is None:
            msg = f"Parameter {self.name} has no unit"
            raise ValueError(msg)
        return self


class URL(Parameter):
    """URL parameter."""

    name: str = "URL"
    short_name: str = "URL"
    mandatory: bool = True
    validate_on: list[str] = ["username", "password", "private_token"]
    type: ParameterType = ParameterType.URL


class LandingURL(StringParameter):
    """URL to a human readable version of a CSV, XML, or JSON report.

    This is a string parameter because Quality-time doesn't validate these URLs.
    """

    short_name: str = "URL"


class SingleChoiceParameter(Parameter):
    """Single choice parameter."""

    type: ParameterType = ParameterType.SINGLE_CHOICE


class MultipleChoiceWithDefaultsParameter(Parameter):
    """Multiple choice parameter with default value.

    If the default value is not set, the default value equals all possible values.
    """

    type: ParameterType = ParameterType.MULTIPLE_CHOICE_WITH_DEFAULTS
    default_value: str | list[str] = []

    @model_validator(mode="after")
    def set_default_value(self) -> Self:
        """Make the default value equal to all values, if it was not set explicitly."""
        if not self.default_value and self.values:
            self.default_value = self.values
        return self


class MultipleChoiceWithoutDefaultsParameter(Parameter):
    """Multiple choice parameter without default value."""

    type: ParameterType = ParameterType.MULTIPLE_CHOICE_WITHOUT_DEFAULTS
    default_value: str | list[str] = []
    placeholder: str = "none"

    @model_validator(mode="after")
    def check_default_value(self) -> Self:
        """Check that the default value is empty."""
        if self.default_value != []:
            msg = f"Parameter {self.name} has default value {self.default_value}, should be an empty list"
            raise ValueError(msg)
        return self


class MultipleChoiceWithAdditionParameter(MultipleChoiceWithDefaultsParameter):
    """Multiple choice parameter that allows the user to add additional options."""

    type: ParameterType = ParameterType.MULTIPLE_CHOICE_WITH_ADDITION
    placeholder: str = "none"


class Username(StringParameter):
    """User to be used for authentication."""

    name: str = "Username for basic authentication"
    short_name: str = "username"


class Password(Parameter):
    """Password parameter."""

    name: str = "Password for basic authentication"
    short_name: str = "password"
    type: ParameterType = ParameterType.PASSWORD


class PrivateToken(Password):
    """Private token for authentication."""

    name: str = "Private token"
    short_name: str = "private token"
    validation_path: str = ""  # URL path to use for the validation of tokens


class APIVersion(SingleChoiceParameter):
    """API version to use."""

    name: str = "API version"
    mandatory: bool = True
    help: str | None = "Version of the API (application programming interface) to use for retrieving information."


class Days(IntegerParameter):
    """Number of days parameter."""

    unit: Unit = Unit.DAYS
    min_value: str = "1"


class FixAvailability(MultipleChoiceWithDefaultsParameter):
    """Fix availability for security warnings."""

    name: str = "Fix availability"
    placeholder: str | None = "disregard fix availability"
    metrics: list[str] = ["security_warnings"]
    help: str | None = "Show security warnings without fix, with fix, or both."
    values: list[str] | None = ["fix available", "no fix available"]


class Severities(MultipleChoiceWithDefaultsParameter):
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


class TestResult(MultipleChoiceWithDefaultsParameter):
    """Test result parameter."""

    name: str = "Test results"
    help: str = (
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
    help: str = "Only count merge requests with fewer than the minimum number of upvotes."
    unit: Unit = Unit.UPVOTES
    metrics: list[str] = ["merge_requests"]


class Branch(StringParameter):
    """Branch name parameter."""

    name: str = "Branch"
    default_value: str | list[str] = "main"
    metrics: list[str] = ["source_up_to_dateness"]


class Branches(MultipleChoiceWithAdditionParameter):
    """Branches parameter."""

    name: str = "Branches (regular expressions or branch names)"
    short_name: str = "branches"
    placeholder: str = "all branches"
    metrics: list[str] = ["pipeline_duration"]


class BranchesToIgnore(MultipleChoiceWithAdditionParameter):
    """Branches to ignore parameter."""

    name: str = "Branches to ignore (regular expressions or branch names)"
    short_name: str = "branches to ignore"
    metrics: list[str] = ["inactive_branches"]


class TargetBranchesToInclude(MultipleChoiceWithAdditionParameter):
    """Target branches to include parameter."""

    name: str = "Target branches to include (regular expressions or branch names)"
    short_name: str = "target branches to include"
    placeholder: str = "all target branches"
    metrics: list[str] = ["merge_requests"]


class BranchMergeStatus(MultipleChoiceWithDefaultsParameter):
    """Branch merge status."""

    name: str = "Branch merge status"
    short_name: str = "merge status"
    help: str = "Limit which merge states to count."
    placeholder: str = "all merge states"
    metrics: list[str] = ["inactive_branches"]
    values: list[str] = ["merged", "unmerged"]


class MergeRequestState(MultipleChoiceWithDefaultsParameter):
    """Merge request states parameter."""

    name: str = "Merge request states"
    short_name: str = "states"
    help: str = "Limit which merge request states to count."
    placeholder: str = "all states"
    metrics: list[str] = ["merge_requests"]


class FailureType(MultipleChoiceWithDefaultsParameter):
    """Failure type parameter."""

    name: str = "Failure types"
    help: str = "Limit which failure types to count as failed."
    placeholder: str = "all failure types"
    metrics: list[str] = ["failed_jobs"]


class ResultType(MultipleChoiceWithDefaultsParameter):
    """Build result type parameter."""

    name: str = "Build result types"
    short_name: str = "result types"
    help: str = "Limit which build result types to include."
    placeholder: str = "all result types"
    metrics: list[str] = ["job_runs_within_time_period"]


class TransactionsToIgnore(MultipleChoiceWithAdditionParameter):
    """Transactions to ignore parameter."""

    name: str = "Transactions to ignore (regular expressions or transaction names)"
    short_name: str = "transactions to ignore"
    help: str = "Transactions to ignore can be specified by transaction name or by regular expression."
    metrics: list[str] = ["slow_transactions", "tests"]


class TransactionsToInclude(MultipleChoiceWithAdditionParameter):
    """Transactions to include parameter."""

    name: str = "Transactions to include (regular expressions or transaction names)"
    short_name: str = "transactions to include"
    help: str = "Transactions to include can be specified by transaction name or by regular expression."
    placeholder: str = "all transactions"
    metrics: list[str] = ["slow_transactions", "tests"]


PERCENTILE_50, PERCENTILE_75, PERCENTILE_90, PERCENTILE_95, PERCENTILE_98, PERCENTILE_99 = (
    f"{percentile}th percentile" for percentile in (50, 75, 90, 95, 98, 99)
)


class ResponseTimeToEvaluate(SingleChoiceParameter):
    """Response time to evaluate parameter."""

    name: str = "Response time type to evaluate against the target response time"
    short_name: str = "response time types to evaluate"
    help: str = "Which response time type to compare with the target response time to determine slow transactions."
    metrics: list[str] = ["slow_transactions"]


class TargetResponseTime(IntegerParameter):
    """Target response time parameter."""

    name: str = "Target response time"
    short_name: str = "target response time"
    help: str = "The response times of the transactions should be less than or equal to the target response time."
    default_value: str = "1000"
    unit: str = "milliseconds"
    metrics: list[str] = ["slow_transactions"]


class TransactionSpecificTargetResponseTimes(MultipleChoiceWithAdditionParameter):
    """Transaction-specific target response times parameter."""

    name: str = (
        "Transaction-specific target response times (regular expressions or transaction names:target response time)"
    )
    short_name: str = "transactions-specific target response times"
    help: str = (
        "Transactions-specific target responses times (in milliseconds) can be specified by transaction name or by "
        "regular expression, separated from the target response time by a colon, e.g.: '/api/v?/search/.*:1500'."
    )
    placeholder: str = "none"
    metrics: list[str] = ["slow_transactions"]


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
        source_type = source_type.removeprefix("an ")
        format_phrase = f" in {source_type_format} format" if source_type_format else ""
        url_kwargs["name"] = (
            f"URL to {source_type_article} {source_type}{format_phrase} or to a zip with {source_type}s{format_phrase}"
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
