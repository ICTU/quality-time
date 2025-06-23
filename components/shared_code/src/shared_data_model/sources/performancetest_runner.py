"""Performancetest-runner source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    MultipleChoiceParameter,
    TestResult,
    TransactionsToIgnore,
    TransactionsToInclude,
    access_parameters,
)

ALL_PERFORMANCETEST_RUNNER_METRICS = [
    "performancetest_duration",
    "performancetest_stability",
    "scalability",
    "slow_transactions",
    "software_version",
    "source_up_to_dateness",
    "tests",
]

PERFORMANCETEST_RUNNER = Source(
    name="Performancetest-runner",
    description="An open source tool to run performancetests and create performancetest reports.",
    url=HttpUrl("https://github.com/ICTU/performancetest-runner"),
    parameters={
        "test_result": TestResult(values=["failed", "success"]),
        "thresholds": MultipleChoiceParameter(
            name="Thresholds",
            help="If provided, only count transactions that surpass the selected thresholds.",
            placeholder="all thresholds",
            values=["high", "warning"],
            api_values={"high": "red", "warning": "yellow"},
            metrics=["slow_transactions"],
        ),
        "transactions_to_ignore": TransactionsToIgnore(),
        "transactions_to_include": TransactionsToInclude(),
        **access_parameters(
            ALL_PERFORMANCETEST_RUNNER_METRICS,
            source_type="Performancetest-runner report",
            source_type_format="HTML",
            include={"landing_url": False},
        ),
    },
    entities={
        "slow_transactions": Entity(
            name="slow transaction",
            attributes=[
                EntityAttribute(name="Transaction", key="name"),
                EntityAttribute(name="Threshold", color={"high": Color.NEGATIVE, "warning": Color.WARNING}),
            ],
        ),
    },
)
