"""Junit XML source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import TestResult, access_parameters

ALL_JUNIT_METRICS = ["source_up_to_dateness", "test_cases", "test_suites", "tests"]

RESULT_COLORS = {
    "errored": Color.NEGATIVE,
    "failed": Color.NEGATIVE,
    "passed": Color.POSITIVE,
    "skipped": Color.WARNING,
}

TEST_ENTITY = Entity(
    name="test",
    attributes=[
        EntityAttribute(name="Class name"),
        EntityAttribute(name="Host name"),
        EntityAttribute(name="Test case", key="name"),
        EntityAttribute(name="Test result", color=RESULT_COLORS),
    ],
)

JUNIT = Source(
    name="JUnit XML report",
    description="Test reports in the JUnit XML format.",
    url=HttpUrl("https://junit.org/junit5/"),
    parameters={
        "test_result": TestResult(metrics=["test_suites", "tests"], values=["errored", "failed", "passed", "skipped"]),
        **access_parameters(ALL_JUNIT_METRICS, source_type="JUnit report", source_type_format="XML"),
    },
    entities={
        "test_cases": TEST_ENTITY,
        "test_suites": Entity(
            name="test",
            attributes=[
                EntityAttribute(name="Suite name"),
                EntityAttribute(name="Suite result", color=RESULT_COLORS),
                EntityAttribute(name="Tests", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Passed", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Errored", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Failed", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Skipped", type=EntityAttributeType.INTEGER),
            ],
        ),
        "tests": TEST_ENTITY,
    },
)
