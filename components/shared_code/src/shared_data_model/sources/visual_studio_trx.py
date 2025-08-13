"""Visual Studio test result file (.trx) source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import TestResult, TestResultAggregationStrategy, access_parameters

ALL_VISUAL_STUDIO_TRX_METRICS = ["source_up_to_dateness", "test_cases", "tests"]

TEST_ENTITIES = Entity(
    name="test",
    attributes=[
        EntityAttribute(name="Unittest name", key="name"),
        EntityAttribute(
            name="Test result",
            color={
                "Aborted": Color.NEGATIVE,
                "Completed": Color.POSITIVE,
                "Disconnected": Color.NEGATIVE,
                "Error": Color.NEGATIVE,
                "Failed": Color.NEGATIVE,
                "Inconclusive": Color.WARNING,
                "InProgress": Color.WARNING,
                "NotExecuted": Color.WARNING,
                "NotRunnable": Color.WARNING,
                "Passed": Color.POSITIVE,
                "PassedButRunAborted": Color.POSITIVE,
                "Pending": Color.WARNING,
                "Timeout": Color.NEGATIVE,
                "Warning": Color.WARNING,
            },
        ),
    ],
)

VISUAL_STUDIO_TRX = Source(
    name="Visual Studio TRX",
    description="Test reports in the Visual Studio TRX format.",
    url=HttpUrl(
        "https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-platform-extensions-test-reports#"
        "visual-studio-test-reports"
    ),
    parameters={
        "test_result": TestResult(
            values=[
                "Aborted",
                "Completed",
                "Disconnected",
                "Error",
                "Failed",
                "Inconclusive",
                "InProgress",
                "NotExecuted",
                "NotRunnable",
                "Passed",
                "PassedButRunAborted",
                "Pending",
                "Timeout",
                "Warning",
            ],
        ),
        "test_result_aggregation_strategy": TestResultAggregationStrategy(),
        **access_parameters(ALL_VISUAL_STUDIO_TRX_METRICS, source_type="Visual Studio TRX", source_type_format="XML"),
    },
    entities={"tests": TEST_ENTITIES, "test_cases": TEST_ENTITIES},
)
