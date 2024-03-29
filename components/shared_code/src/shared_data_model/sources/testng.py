"""TestNG source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import TestResult, access_parameters

ALL_TESTNG_METRICS = ["source_up_to_dateness", "test_cases", "tests"]

TEST_ENTITIES = Entity(
    name="test",
    attributes=[
        EntityAttribute(name="Class name"),
        EntityAttribute(name="Test method", key="name"),
        EntityAttribute(name="Description"),
        EntityAttribute(
            name="Test result",
            color={"failed": Color.NEGATIVE, "passed": Color.POSITIVE, "skipped": Color.WARNING},
        ),
    ],
)

TESTNG = Source(
    name="TestNG",
    description="Test reports in the TestNG XML format.",
    url=HttpUrl("https://testng.org"),
    parameters={
        "test_result": TestResult(values=["failed", "ignored", "passed", "skipped"]),
        **access_parameters(ALL_TESTNG_METRICS, source_type="TestNG report", source_type_format="XML"),
    },
    entities={"tests": TEST_ENTITIES, "test_cases": TEST_ENTITIES},
)
