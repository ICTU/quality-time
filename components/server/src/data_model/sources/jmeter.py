"""JMeter sources."""

from ..meta.entity import EntityAttributeType
from ..meta.source import Source
from ..parameters import (
    access_parameters,
    IntegerParameter,
    MultipleChoiceWithAdditionParameter,
    SingleChoiceParameter,
    TestResult,
)


ALL_JMETER_METRICS = ["slow_transactions", "tests"]

JMETER_URL = "https://jmeter.apache.org"

JMETER_DESCRIPTION = (
    "Apache JMeter application is open source software, a 100% pure Java application designed to "
    "load test functional behavior and measure performance."
)

TRANSACTIONS_TO_IGNORE = MultipleChoiceWithAdditionParameter(
    name="Transactions to ignore (regular expressions or transaction names)",
    short_name="transactions to ignore",
    help="Transactions to ignore can be specified by transaction name or by regular expression.",
    metrics=ALL_JMETER_METRICS,
)

TRANSACTIONS_TO_INCLUDE = MultipleChoiceWithAdditionParameter(
    name="Transactions to include (regular expressions or transaction names)",
    short_name="transactions to include",
    help="Transactions to include can be specified by transaction name or by regular expression.",
    placeholder="all",
    metrics=ALL_JMETER_METRICS,
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

RESPONSE_TIME_TO_EVALUATE = SingleChoiceParameter(
    name="Response time type to evaluate against the target response time",
    short_name="response time types to evaluate",
    help="Which response time type to compare with the target response time to determine slow transactions.",
    default_value=PERCENTILE_90,
    values=[PERCENTILE_90, "mean", "median", "minimum", "maximum"],
    api_values={
        PERCENTILE_90: "percentile_90_response_time",
        "mean": "mean_response_time",
        "median": "median_response_time",
        "minimum": "min_response_time",
        "maximum": "max_response_time",
    },
    metrics=["slow_transactions"],
)

ENTITIES = dict(
    slow_transactions=dict(
        name="slow transaction",
        attributes=[
            dict(name="Transactions", key="name"),
            dict(name="Sample count", type=EntityAttributeType.INTEGER),
            dict(name="Error count", type=EntityAttributeType.INTEGER),
            dict(name="Error percentage", type=EntityAttributeType.FLOAT),
            dict(name="Mean response time (ms)", key="mean_response_time", type=EntityAttributeType.FLOAT),
            dict(name="Median response time (ms)", key="median_response_time", type=EntityAttributeType.FLOAT),
            dict(name="Minimum response time (ms)", key="min_response_time", type=EntityAttributeType.FLOAT),
            dict(name="Maximum response time (ms)", key="max_response_time", type=EntityAttributeType.FLOAT),
            dict(
                name="90th percentile response time (ms)",
                key="percentile_90_response_time",
                type=EntityAttributeType.FLOAT,
            ),
        ],
    )
)

JMETER_CSV = Source(
    name="JMeter CSV",
    description=JMETER_DESCRIPTION,
    url=JMETER_URL,
    parameters=dict(
        response_time_to_evaluate=RESPONSE_TIME_TO_EVALUATE,
        target_response_time=TARGET_RESPONSE_TIME,
        transaction_specific_target_response_times=TRANSACTION_SPECIFIC_TARGET_RESPONSE_TIMES,
        transactions_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Transactions to ignore (regular expressions or transaction names)",
            short_name="transactions to ignore",
            help="Transactions to ignore can be specified by transaction name or by regular expression.",
            metrics=["slow_transactions"],
        ),
        transactions_to_include=MultipleChoiceWithAdditionParameter(
            name="Transactions to include (regular expressions or transaction names)",
            short_name="transactions to include",
            help="Transactions to include can be specified by transaction name or by regular expression.",
            placeholder="all",
            metrics=["slow_transactions"],
        ),
        **access_parameters(["slow_transactions"], source_type="JMeter report", source_type_format="CSV")
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
        **access_parameters(ALL_JMETER_METRICS, source_type="JMeter report", source_type_format="JSON")
    ),
    entities=ENTITIES,
)
