"""Gatling sources."""

from ..meta.source import Source
from ..parameters import access_parameters, MultipleChoiceWithAdditionParameter, SingleChoiceParameter

from .jmeter import TARGET_RESPONSE_TIME, TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES, PERCENTILE_95, PERCENTILE_99


GATLING_JSON_METRICS = ["slow_transactions"]
GATLING_URL = "https://gatling.io"
GATLING_DESCRIPTION = (
    "Gatling is an open-source load testing solution, designed for continuous load testing and development pipeline "
    "integration."
)

TRANSACTIONS_TO_IGNORE = MultipleChoiceWithAdditionParameter(
    name="Transactions to ignore (regular expressions or transaction names)",
    short_name="transactions to ignore",
    help="Transactions to ignore can be specified by transaction name or by regular expression.",
    metrics=GATLING_JSON_METRICS,
)

TRANSACTIONS_TO_INCLUDE = MultipleChoiceWithAdditionParameter(
    name="Transactions to include (regular expressions or transaction names)",
    short_name="transactions to include",
    help="Transactions to include can be specified by transaction name or by regular expression.",
    placeholder="all",
    metrics=GATLING_JSON_METRICS,
)

PERCENTILE_50 = "50th percentile"
PERCENTILE_75 = "75th percentile"

RESPONSE_TIME_TO_EVALUATE = SingleChoiceParameter(
    name="Response time type to evaluate against the target response time",
    short_name="response time types to evaluate",
    help="Which response time type to compare with the target response time to determine slow transactions.",
    default_value=PERCENTILE_95,
    values=[PERCENTILE_50, PERCENTILE_75, PERCENTILE_95, PERCENTILE_99, "mean", "median", "minimum", "maximum"],
    api_values={
        PERCENTILE_50: "percentile_50_response_time",
        PERCENTILE_75: "percentile_75_response_time",
        PERCENTILE_95: "percentile_95_response_time",
        PERCENTILE_99: "percentile_99_response_time",
        "mean": "mean_response_time",
        "median": "median_response_time",
        "minimum": "min_response_time",
        "maximum": "max_response_time",
    },
    metrics=["slow_transactions"],
)

GATLING_JSON = Source(
    name="Gatling JSON",
    description=GATLING_DESCRIPTION,
    url=GATLING_URL,
    parameters=dict(
        response_time_to_evaluate=RESPONSE_TIME_TO_EVALUATE,
        target_response_time=TARGET_RESPONSE_TIME,
        transaction_specific_target_response_times=TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES,
        transactions_to_ignore=TRANSACTIONS_TO_IGNORE,
        transactions_to_include=TRANSACTIONS_TO_INCLUDE,
        **access_parameters(GATLING_JSON_METRICS, source_type="Gatling report", source_type_format="JSON")
    ),
)
