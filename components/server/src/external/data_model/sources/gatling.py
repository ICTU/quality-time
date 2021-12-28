"""Gatling sources."""

from ..meta.source import Source
from ..parameters import access_parameters, SingleChoiceParameter

GATLING_JSON_METRICS = ["slow_transactions"]
GATLING_URL = "https://gatling.io"
GATLING_DESCRIPTION = (
    "Gatling is an open-source load testing solution, designed for continuous load testing and development pipeline "
    "integration."
)

PERCENTILE_90 = "90th percentile"
PERCENTILE_95 = "95th percentile"
PERCENTILE_99 = "99th percentile"

RESPONSE_TIME_TO_EVALUATE = SingleChoiceParameter(
    name="Response time type to evaluate against the target response time",
    short_name="response time types to evaluate",
    help="Which response time type to compare with the target response time to determine slow transactions.",
    default_value=PERCENTILE_90,
    values=[PERCENTILE_90, PERCENTILE_95, PERCENTILE_99, "mean", "median", "minimum", "maximum"],
    api_values={
        PERCENTILE_90: "percentile_90_response_time",
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
        **access_parameters(GATLING_JSON_METRICS, source_type="Gatling report", source_type_format="JSON")
    ),
)
