"""Test cases collector."""

import re
from typing import Optional, Sequence

from base_collectors import MetricCollector
from model import Entity, SourceMeasurement, MetricMeasurement


class TestCases(MetricCollector):
    """Test cases collector."""

    __test__ = False  # Make sure nose knows this is not a test class

    # Mapping to calculate the test result of a test case. The keys are tuples of the current test result of the test
    # case and the next test result found. The value is the resulting test result. For example,
    # {("passed", "skipped"), "skipped"} means that if a test case has passed so far and we see a skipped test result,
    # the updated test result state of the test case is skipped.
    TEST_RESULT_STATE = {
        (None, "passed"): "passed",
        (None, "skipped"): "skipped",
        (None, "failed"): "failed",
        ("passed", "passed"): "passed",
        ("passed", "skipped"): "skipped",
        ("passed", "failed"): "failed",
        ("skipped", "passed"): "skipped",
        ("skipped", "skipped"): "skipped",
        ("skipped", "failed"): "failed",
        ("failed", "passed"): "failed",
        ("failed", "skipped"): "failed",
        ("failed", "failed"): "failed",
    }
    TEST_CASE_KEY_RE = re.compile(r"\w+\-\d+")

    async def collect(self) -> Optional[MetricMeasurement]:
        """Override to combine the logical and the physical test cases."""
        if (measurement := await super().collect()) is None:
            return None
        test_cases = self.test_cases(measurement.sources)
        test_case_keys = set(test_cases.keys())
        for entity in self.test_entities(measurement.sources):
            for test_case_key in self.referenced_test_cases(entity) & test_case_keys:
                test_result_so_far = test_cases[test_case_key].get("test_result")
                test_result = entity["test_result"]
                test_cases[test_case_key]["test_result"] = self.TEST_RESULT_STATE[(test_result_so_far, test_result)]
        for test in self.test_sources(measurement.sources):
            test.value = "0"  # Only count test cases
        return measurement

    @staticmethod
    def test_cases(sources: Sequence[SourceMeasurement]) -> dict[str, Entity]:
        """Return the test cases, indexed by their keys."""
        return {
            entity["issue_key"]: entity for source in sources for entity in source.entities if source.type == "jira"
        }

    @classmethod
    def test_entities(cls, sources: Sequence[SourceMeasurement]) -> list[Entity]:
        """Return the test entities."""
        return [entity for source in cls.test_sources(sources) for entity in source.entities]

    @staticmethod
    def test_sources(sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the test sources."""
        return [source for source in sources if source.type == "testng"]

    @classmethod
    def referenced_test_cases(cls, entity: Entity) -> set[str]:
        """Return the keys of test cases referenced in test entity names or descriptions."""
        text_attributes = " ".join(entity.get(attribute_key, "") for attribute_key in ("name", "description"))
        return set(re.findall(cls.TEST_CASE_KEY_RE, text_attributes))
