"""Grafana k6 sources."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    PERCENTILE_90,
    PERCENTILE_95,
    PERCENTILE_98,
    PERCENTILE_99,
    ResponseTimeToEvaluate,
    TargetResponseTime,
    TestResult,
    TransactionSpecificTargetResponseTimes,
    TransactionsToIgnore,
    TransactionsToInclude,
    access_parameters,
)

FLOAT = EntityAttributeType.FLOAT
HELP = "response time (milliseconds)"
ALL_GRAFANA_K6_METRICS = [
    "performancetest_duration",
    "slow_transactions",
    "source_up_to_dateness",
    "source_version",
    "tests",
]

DEFAULT_THRESHOLD_TO_EVALUATE = "none (use thresholds in summary.json)"
RESPONSE_TIME_TO_EVALUATE = ResponseTimeToEvaluate(
    default_value=DEFAULT_THRESHOLD_TO_EVALUATE,
    values=[
        PERCENTILE_90,
        PERCENTILE_95,
        PERCENTILE_98,
        PERCENTILE_99,
        "average",
        "median",
        "minimum",
        "maximum",
        DEFAULT_THRESHOLD_TO_EVALUATE,
    ],
    api_values={
        "average": "average_response_time",
        "median": "median_response_time",
        "minimum": "min_response_time",
        "maximum": "max_response_time",
    },
)

GRAFANA_K6 = Source(
    name="Grafana k6",
    description=(
        "K6 is an open-source load testing tool developed by Grafana Labs. It is designed to help developers test "
        "the performance and reliability of their systems."
    ),
    documentation={
        "slow_transactions": """When using Grafana k6 as source, only Grafana k6 metrics whose `contains` field equals
`"time"` are considered. Other metrics are ignored. To count the test results of Grafana k6 metrics (passed, failed,
or both) based on their thresholds, use the [test results](#test-results) metric.""",
        "tests": """When using Grafana k6 as source, only Grafana k6 metrics that have at least one threshold are
counted as test. Other metrics are ignored. A test passes if all thresholds are `ok`; it fails if one or more
thresholds are not `ok`. To count the number of Grafana k6 metrics slower than their target response time, use the
[slow transactions](#slow-transactions) metric.""",
    },
    url=HttpUrl("https://k6.io"),
    parameters={
        "response_time_to_evaluate": RESPONSE_TIME_TO_EVALUATE,
        "target_response_time": TargetResponseTime(),
        "test_result": TestResult(values=["failed", "passed"]),
        "transaction_specific_target_response_times": TransactionSpecificTargetResponseTimes(),
        "transactions_to_ignore": TransactionsToIgnore(metrics=["slow_transactions"]),
        "transactions_to_include": TransactionsToInclude(metrics=["slow_transactions"]),
        **access_parameters(ALL_GRAFANA_K6_METRICS, source_type="Grafana k6 summary.json", source_type_format="JSON"),
    },
    entities={
        "slow_transactions": Entity(
            name="slow transaction",
            attributes=[
                EntityAttribute(name="Transaction", key="name"),
                EntityAttribute(name="Thresholds"),
                EntityAttribute(name="Sample count", key="count", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Average", help=f"Average {HELP}", key="average_response_time", type=FLOAT),
                EntityAttribute(name="Median", help=f"Median {HELP}", key="median_response_time", type=FLOAT),
                EntityAttribute(name="Minimum", help=f"Minimum {HELP}", key="min_response_time", type=FLOAT),
                EntityAttribute(name="Maximum", help=f"Maximum {HELP}", key="max_response_time", type=FLOAT),
            ],
        )
    },
)
