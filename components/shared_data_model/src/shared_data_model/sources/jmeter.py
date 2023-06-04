"""JMeter sources."""

from shared_data_model.meta.entity import EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    IntegerParameter,
    MultipleChoiceWithAdditionParameter,
    SingleChoiceParameter,
    TestResult,
    access_parameters,
)

JMETER_JSON_METRICS = ["slow_transactions", "tests"]
JMETER_CSV_METRICS = [*JMETER_JSON_METRICS, "performancetest_duration", "source_up_to_dateness"]

JMETER_URL = "https://jmeter.apache.org"

JMETER_DESCRIPTION = (
    "Apache JMeter application is open source software, a 100% pure Java application designed to "
    "load test functional behavior and measure performance."
)

TRANSACTIONS_TO_IGNORE = MultipleChoiceWithAdditionParameter(
    name="Transactions to ignore (regular expressions or transaction names)",
    short_name="transactions to ignore",
    help="Transactions to ignore can be specified by transaction name or by regular expression.",
    metrics=JMETER_JSON_METRICS,
)

TRANSACTIONS_TO_INCLUDE = MultipleChoiceWithAdditionParameter(
    name="Transactions to include (regular expressions or transaction names)",
    short_name="transactions to include",
    help="Transactions to include can be specified by transaction name or by regular expression.",
    placeholder="all",
    metrics=JMETER_JSON_METRICS,
)

TARGET_RESPONSE_TIME = IntegerParameter(
    name="Target response time",
    short_name="target response time",
    help="The response times of the transactions should be less than or equal to the target response time.",
    default_value="1000",
    unit="milliseconds",
    metrics=["slow_transactions"],
)

TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES = MultipleChoiceWithAdditionParameter(
    name="Transaction-specific target response times (regular expressions or transaction names:target response time)",
    short_name="transactions-specific target response times",
    help="Transactions-specific target responses times (in milliseconds) can be specified by transaction name or by "
    "regular expression, separated from the target response time by a colon, e.g.: '/api/v?/search/.*:1500'.",
    placeholder="none",
    metrics=["slow_transactions"],
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

# Slow transaction entity attributes:
INTEGER, FLOAT = EntityAttributeType.INTEGER, EntityAttributeType.FLOAT
HELP = "response time (milliseconds)"
JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES = [
    {"name": "Transactions", "key": "name"},
    {"name": "Sample count", "type": INTEGER},
    {"name": "Error count", "type": INTEGER},
    {"name": "Error percentage", "type": FLOAT},
    {"name": "Mean", "help": f"Mean {HELP}", "key": "mean_response_time", "type": FLOAT},
    {"name": "Median", "help": f"Median {HELP}", "key": "median_response_time", "type": FLOAT},
    {"name": "Minimum", "help": f"Minimum {HELP}", "key": "min_response_time", "type": FLOAT},
    {"name": "Maximum", "help": f"Maximum {HELP}", "key": "max_response_time", "type": FLOAT},
    {"name": PERCENTILE_90, "help": f"{PERCENTILE_90} {HELP}", "key": "percentile_90_response_time", "type": FLOAT},
    {"name": PERCENTILE_95, "help": f"{PERCENTILE_95} {HELP}", "key": "percentile_95_response_time", "type": FLOAT},
    {"name": PERCENTILE_99, "help": f"{PERCENTILE_99} {HELP}", "key": "percentile_99_response_time", "type": FLOAT},
]

ENTITIES = {
    "slow_transactions": {
        "name": "slow transaction",
        "attributes": JMETER_SLOW_TRANSACTION_ENTITY_ATTRIBUTES,
    },
}

JMETER_CSV = Source(
    name="JMeter CSV",
    description=JMETER_DESCRIPTION,
    url=JMETER_URL,
    parameters=dict(
        test_result=TestResult(values=["failed", "success"]),
        response_time_to_evaluate=RESPONSE_TIME_TO_EVALUATE,
        target_response_time=TARGET_RESPONSE_TIME,
        transaction_specific_target_response_times=TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES,
        transactions_to_ignore=TRANSACTIONS_TO_IGNORE,
        transactions_to_include=TRANSACTIONS_TO_INCLUDE,
        **access_parameters(JMETER_CSV_METRICS, source_type="JMeter report", source_type_format="CSV"),
    ),
    entities=ENTITIES,
)

JMETER_JSON = Source(
    name="JMeter JSON",
    description=JMETER_DESCRIPTION,
    url=JMETER_URL,
    parameters=dict(
        test_result=TestResult(values=["failed", "success"]),
        response_time_to_evaluate=RESPONSE_TIME_TO_EVALUATE,
        target_response_time=TARGET_RESPONSE_TIME,
        transaction_specific_target_response_times=TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES,
        transactions_to_ignore=TRANSACTIONS_TO_IGNORE,
        transactions_to_include=TRANSACTIONS_TO_INCLUDE,
        **access_parameters(JMETER_JSON_METRICS, source_type="JMeter report", source_type_format="JSON"),
    ),
    entities=ENTITIES,
)
