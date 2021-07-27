"""Junit XML source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, TestResult


ALL_JUNIT_METRICS = ["source_up_to_dateness", "test_cases", "tests"]

TEST_ENTITIES = dict(
    name="test",
    attributes=[
        dict(name="Class name"),
        dict(name="Test case", key="name"),
        dict(
            name="Test result",
            color=dict(errored=Color.NEGATIVE, failed=Color.NEGATIVE, passed=Color.POSITIVE, skipped=Color.WARNING),
        ),
    ],
)

JUNIT = Source(
    name="JUnit XML report",
    description="Test reports in the JUnit XML format.",
    url="https://junit.org",
    parameters=dict(
        test_result=TestResult(values=["errored", "failed", "passed", "skipped"]),
        **access_parameters(ALL_JUNIT_METRICS, source_type="JUnit report", source_type_format="XML")
    ),
    entities=dict(tests=TEST_ENTITIES, test_cases=TEST_ENTITIES),
)
