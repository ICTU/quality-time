"""Performancetest-runner source."""

from shared_data_model.meta.entity import Color
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    TestResult,
    access_parameters,
)

TRANSACTION_METRICS = ["slow_transactions", "tests"]
ALL_PERFORMANCETEST_RUNNER_METRICS = [
    *TRANSACTION_METRICS,
    "performancetest_duration",
    "performancetest_stability",
    "scalability",
    "software_version",
    "source_up_to_dateness",
]

PERFORMANCETEST_RUNNER = Source(
    name="Performancetest-runner",
    description="An open source tool to run performancetests and create performancetest reports.",
    url="https://github.com/ICTU/performancetest-runner",
    parameters=dict(
        test_result=TestResult(values=["failed", "success"]),
        thresholds=MultipleChoiceParameter(
            name="Thresholds",
            help="If provided, only count transactions that surpass the selected thresholds.",
            placeholder="all thresholds",
            values=["high", "warning"],
            api_values={"high": "red", "warning": "yellow"},
            metrics=["slow_transactions"],
        ),
        transactions_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Transactions to ignore (regular expressions or transaction names)",
            short_name="transactions to ignore",
            help="Transactions to ignore can be specified by transaction name or by regular expression.",
            metrics=TRANSACTION_METRICS,
        ),
        transactions_to_include=MultipleChoiceWithAdditionParameter(
            name="Transactions to include (regular expressions or transaction names)",
            short_name="transactions to include",
            help="Transactions to include can be specified by transaction name or by regular expression.",
            placeholder="all",
            metrics=TRANSACTION_METRICS,
        ),
        **access_parameters(
            ALL_PERFORMANCETEST_RUNNER_METRICS,
            source_type="Performancetest-runner report",
            source_type_format="HTML",
            include={"landing_url": False},
        ),
    ),
    entities={
        "slow_transactions": {
            "name": "slow transaction",
            "attributes": [
                {"name": "Transaction", "key": "name"},
                {"name": "Threshold", "color": {"high": Color.NEGATIVE, "warning": Color.WARNING}},
            ],
        },
    },
)
