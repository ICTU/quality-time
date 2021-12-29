"""Gatling sources."""

from ..meta.entity import EntityAttributeType
from ..meta.source import Source
from ..parameters import access_parameters, MultipleChoiceWithAdditionParameter, SingleChoiceParameter

from .jmeter import (
    TARGET_RESPONSE_TIME,
    TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES,
    PERCENTILE_95,
    PERCENTILE_99,
    JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES,
)


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
    values=[PERCENTILE_50, PERCENTILE_75, PERCENTILE_95, PERCENTILE_99, "mean", "minimum", "maximum"],
    api_values={
        PERCENTILE_50: "percentile_50_response_time",
        PERCENTILE_75: "percentile_75_response_time",
        PERCENTILE_95: "percentile_95_response_time",
        PERCENTILE_99: "percentile_99_response_time",
        "mean": "mean_response_time",
        "minimum": "min_response_time",
        "maximum": "max_response_time",
    },
    metrics=["slow_transactions"],
)

GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES = JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES.copy()
del GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES[8]  # Remove the 90th percentile attribute
del GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES[5]  # Remove the median attribute
GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES.insert(
    7,
    dict(
        name="50th percentile",
        help="50th percentile response time (milliseconds)",
        key="percentile_50_response_time",
        type=EntityAttributeType.FLOAT,
    ),
)
GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES.insert(
    8,
    dict(
        name="75 percentile",
        help="75th percentile response time (milliseconds)",
        key="percentile_75_response_time",
        type=EntityAttributeType.FLOAT,
    ),
)

ENTITIES = dict(
    slow_transactions=dict(
        name="slow transaction",
        attributes=GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES,
    )
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
        **access_parameters(
            GATLING_JSON_METRICS,
            source_type="Gatling report",
            source_type_format="JSON",
            kwargs=dict(
                url=dict(
                    help="The Gatling report in JSON format is a file called 'stats.json' located in the 'js' folder "
                    "of a Gatling HTML report"
                )
            ),
        )
    ),
    entities=ENTITIES,
)
