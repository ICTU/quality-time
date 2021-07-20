"""TestNG source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, TestResult


ALL_TESTNG_METRICS = ["source_up_to_dateness", "tests"]

TESTNG = Source(
    name="TestNG",
    description="Test reports in the TestNG XML format.",
    url="https://testng.org",
    parameters=dict(
        test_result=TestResult(values=["failed", "ignored", "passed", "skipped"]),
        **access_parameters(ALL_TESTNG_METRICS, source_type="TestNG report", source_type_format="XML")
    ),
    entities=dict(
        tests=dict(
            name="test",
            attributes=[
                dict(name="Class name"),
                dict(name="Test method", key="name"),
                dict(
                    name="Test result",
                    color=dict(failed=Color.NEGATIVE, passed=Color.POSITIVE, skipped=Color.WARNING),
                ),
            ],
        )
    ),
)
