"""Gatling sources."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    PERCENTILE_50,
    PERCENTILE_75,
    PERCENTILE_95,
    PERCENTILE_99,
    ResponseTimeToEvaluate,
    TargetResponseTime,
    TestResult,
    TransactionSpecificTargetResponseTimes,
    TransactionsToIgnore,
    TransactionsToInclude,
    access_parameters,
)

from .jmeter import JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES

GATLING_JSON_METRICS = ["slow_transactions", "tests"]
GATLING_LOG_METRICS = ["performancetest_duration", "source_up_to_dateness", "source_version"]
GATLING_METRICS = GATLING_JSON_METRICS + GATLING_LOG_METRICS
GATLING_URL = HttpUrl("https://gatling.io")
GATLING_DESCRIPTION = (
    "Gatling is an open-source load testing solution, designed for continuous load testing and development pipeline "
    "integration."
)

RESPONSE_TIME_TO_EVALUATE = ResponseTimeToEvaluate(
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
)

GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES = JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES.copy()
del GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES[8]  # Remove the 90th percentile attribute
del GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES[5]  # Remove the median attribute
GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES.insert(
    7,
    EntityAttribute(
        name="50th percentile",
        help="50th percentile response time (milliseconds)",
        key="percentile_50_response_time",
        type=EntityAttributeType.FLOAT,
    ),
)
GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES.insert(
    8,
    EntityAttribute(
        name="75th percentile",
        help="75th percentile response time (milliseconds)",
        key="percentile_75_response_time",
        type=EntityAttributeType.FLOAT,
    ),
)

ENTITIES = {
    "slow_transactions": Entity(
        name="slow transaction",
        attributes=GATLING_SLOW_TRANSACTION_ENTITY_ATTRIBUTES,
    ),
}

GATLING = Source(
    name="Gatling",
    description=GATLING_DESCRIPTION,
    url=GATLING_URL,
    parameters={
        "test_result": TestResult(values=["failed", "success"]),
        "response_time_to_evaluate": RESPONSE_TIME_TO_EVALUATE,
        "target_response_time": TargetResponseTime(),
        "transaction_specific_target_response_times": TransactionSpecificTargetResponseTimes(),
        "transactions_to_ignore": TransactionsToIgnore(),
        "transactions_to_include": TransactionsToInclude(),
        **access_parameters(GATLING_METRICS, source_type="Gatling report", source_type_format="HTML"),
    },
    entities=ENTITIES,
)
