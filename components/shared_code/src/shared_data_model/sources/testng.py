"""TestNG source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import TestResult, TestResultAggregationStrategy, access_parameters

ALL_TESTNG_METRICS = ["source_up_to_dateness", "test_cases", "test_suites", "tests"]

RESULT_COLORS = {"failed": Color.NEGATIVE, "passed": Color.POSITIVE, "skipped": Color.WARNING}

TEST_ENTITY = Entity(
    name="test",
    attributes=[
        EntityAttribute(name="Class name"),
        EntityAttribute(name="Test method", key="name"),
        EntityAttribute(name="Description"),
        EntityAttribute(name="Test result", color=RESULT_COLORS),
    ],
)

TESTNG = Source(
    name="TestNG",
    description="Test reports in the TestNG XML format.",
    url=HttpUrl("https://testng.org"),
    parameters={
        "test_result": TestResult(metrics=["test_suites", "tests"], values=["failed", "ignored", "passed", "skipped"]),
        "test_result_aggregation_strategy": TestResultAggregationStrategy(),
        **access_parameters(ALL_TESTNG_METRICS, source_type="TestNG report", source_type_format="XML"),
    },
    entities={
        "test_cases": TEST_ENTITY,
        "test_suites": Entity(
            name="test suite",
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
