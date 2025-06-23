"""JMeter sources."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    PERCENTILE_90,
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

JSON_METRICS = ["slow_transactions", "tests"]
CSV_METRICS = [*JSON_METRICS, "performancetest_duration", "source_up_to_dateness"]

URL = HttpUrl("https://jmeter.apache.org")

DESCRIPTION = (
    "Apache JMeter application is open source software, a 100% pure Java application designed to "
    "load test functional behavior and measure performance."
)

RESPONSE_TIME_TO_EVALUATE = ResponseTimeToEvaluate(
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
)

# Slow transaction entity attributes:
INTEGER, FLOAT = EntityAttributeType.INTEGER, EntityAttributeType.FLOAT
HELP = "response time (milliseconds)"
JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES = [
    EntityAttribute(name="Transactions", key="name"),
    EntityAttribute(name="Sample count", type=INTEGER),
    EntityAttribute(name="Error count", type=INTEGER),
    EntityAttribute(name="Error percentage", type=FLOAT),
    EntityAttribute(name="Mean", help=f"Mean {HELP}", key="mean_response_time", type=FLOAT),
    EntityAttribute(name="Median", help=f"Median {HELP}", key="median_response_time", type=FLOAT),
    EntityAttribute(name="Minimum", help=f"Minimum {HELP}", key="min_response_time", type=FLOAT),
    EntityAttribute(name="Maximum", help=f"Maximum {HELP}", key="max_response_time", type=FLOAT),
    EntityAttribute(name=PERCENTILE_90, help=f"{PERCENTILE_90} {HELP}", key="percentile_90_response_time", type=FLOAT),
    EntityAttribute(name=PERCENTILE_95, help=f"{PERCENTILE_95} {HELP}", key="percentile_95_response_time", type=FLOAT),
    EntityAttribute(name=PERCENTILE_99, help=f"{PERCENTILE_99} {HELP}", key="percentile_99_response_time", type=FLOAT),
]

ENTITIES = {
    "slow_transactions": Entity(
        name="slow transaction",
        attributes=JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES,
    ),
}

PARAMETERS = {
    "test_result": TestResult(values=["failed", "success"]),
    "response_time_to_evaluate": RESPONSE_TIME_TO_EVALUATE,
    "target_response_time": TargetResponseTime(),
    "transaction_specific_target_response_times": TransactionSpecificTargetResponseTimes(),
    "transactions_to_ignore": TransactionsToIgnore(),
    "transactions_to_include": TransactionsToInclude(),
}

JMETER_CSV = Source(
    name="JMeter CSV",
    description=DESCRIPTION,
    url=URL,
    parameters=PARAMETERS | access_parameters(CSV_METRICS, source_type="JMeter report", source_type_format="CSV"),
    entities=ENTITIES,
)

JMETER_JSON = Source(
    name="JMeter JSON",
    description=DESCRIPTION,
    url=URL,
    parameters=PARAMETERS | access_parameters(JSON_METRICS, source_type="JMeter report", source_type_format="JSON"),
    entities=ENTITIES,
)
