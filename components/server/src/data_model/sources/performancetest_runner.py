"""Performancetest-runner source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import (
    access_parameters,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    TestResult,
)


ALL_PERFORMANCETEST_RUNNER_METRICS = [
    "performancetest_duration",
    "performancetest_stability",
    "scalability",
    "slow_transactions",
    "source_up_to_dateness",
    "tests",
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
            api_values=dict(high="red", warning="yellow"),
            metrics=["slow_transactions"],
        ),
        transactions_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Transactions to ignore (regular expressions or transaction names)",
            short_name="transactions to ignore",
            help="Transactions to ignore can be specified by transaction name or by regular expression.",
            metrics=["slow_transactions", "tests"],
        ),
        transactions_to_include=MultipleChoiceWithAdditionParameter(
            name="Transactions to include (regular expressions or transaction names)",
            short_name="transactions to include",
            help="Transactions to include can be specified by transaction name or by regular expression.",
            placeholder="all",
            metrics=["slow_transactions", "tests"],
        ),
        **access_parameters(
            ALL_PERFORMANCETEST_RUNNER_METRICS,
            source_type="Performancetest-runner report",
            source_type_format="HTML",
            include=dict(landing_url=False),
        )
    ),
    entities=dict(
        slow_transactions=dict(
            name="slow transaction",
            attributes=[
                dict(name="Transaction", key="name"),
                dict(name="Threshold", color=dict(high=Color.NEGATIVE, warning=Color.WARNING)),
            ],
        ),
    ),
)
