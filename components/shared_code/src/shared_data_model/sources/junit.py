"""Junit XML source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import TestResult, access_parameters

ALL_JUNIT_METRICS = ["source_up_to_dateness", "test_cases", "tests"]

TEST_ENTITIES = Entity(
    name="test",
    attributes=[
        EntityAttribute(name="Class name"),
        EntityAttribute(name="Test case", key="name"),
        EntityAttribute(
            name="Test result",
            color={
                "errored": Color.NEGATIVE,
                "failed": Color.NEGATIVE,
                "passed": Color.POSITIVE,
                "skipped": Color.WARNING,
            },
        ),
    ],
)

JUNIT = Source(
    name="JUnit XML report",
    description="Test reports in the JUnit XML format.",
    url=HttpUrl("https://junit.org/junit5/"),
    parameters={
        "test_result": TestResult(values=["errored", "failed", "passed", "skipped"]),
        **access_parameters(ALL_JUNIT_METRICS, source_type="JUnit report", source_type_format="XML"),
    },
    entities={"tests": TEST_ENTITIES, "test_cases": TEST_ENTITIES},
)
