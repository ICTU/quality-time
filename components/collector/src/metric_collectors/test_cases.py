"""Test cases collector."""

import re
from typing import cast, Optional, Sequence

from base_collectors import MetricCollector
from model import Entities, Entity, SourceMeasurement, MetricMeasurement


class TestCases(MetricCollector):
    """Test cases collector."""

    __test__ = False  # Tell nose that this is not a test class

    # Mapping to calculate the test result of a test case. The keys are tuples of the current test result of the test
    # case and the next test result found. The value is the resulting test result. For example,
    # {("passed", "skipped"), "skipped"} means that if a test case has passed so far and we see a skipped test result,
    # the updated test result state of the test case is skipped.
    TEST_RESULT_STATE = {
        ("untested", "passed"): "passed",
        ("untested", "skipped"): "skipped",
        ("untested", "failed"): "failed",
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
        """Override to add the rest results from the test report(s) to the test cases."""
        if (measurement := await super().collect()) is None:
            return None
        test_cases = self.test_cases(measurement.sources)
        test_case_keys = set(test_cases.keys())
        for entity in self.test_entities(measurement.sources):
            for test_case_key in self.referenced_test_cases(entity) & test_case_keys:
                test_result_so_far = test_cases[test_case_key]["test_result"]
                test_result = entity["test_result"]
                test_cases[test_case_key]["test_result"] = self.TEST_RESULT_STATE[(test_result_so_far, test_result)]
        # Set the value of the test sources to zero as this metric only counts test cases
        for test in self.test_sources(measurement.sources):
            test.value = "0"
        # Filter the test cases by test result
        for source in self.test_case_sources(measurement.sources):
            source.entities = Entities(
                entity for entity in source.entities if entity["test_result"] in self.test_results_to_count(source)
            )
            source.value = str(len(source.entities))
        return measurement

    def test_cases(self, sources: Sequence[SourceMeasurement]) -> dict[str, Entity]:
        """Return the test cases, indexed by their keys, with test result initialized to untested."""
        test_cases = {
            entity["issue_key"]: entity for source in self.test_case_sources(sources) for entity in source.entities
        }
        for entity in test_cases.values():
            entity.setdefault("test_result", "untested")
        return test_cases

    def test_case_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the test case sources."""
        return [source for source in sources if self._metric["sources"][source.source_uuid]["type"] == "jira"]

    def test_entities(self, sources: Sequence[SourceMeasurement]) -> list[Entity]:
        """Return the test entities."""
        return [entity for source in self.test_sources(sources) for entity in source.entities]

    def test_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the test sources."""
        return [source for source in sources if self._metric["sources"][source.source_uuid]["type"] == "testng"]

    @classmethod
    def referenced_test_cases(cls, entity: Entity) -> set[str]:
        """Return the keys of test cases referenced in test entity names or descriptions."""
        text_attributes = " ".join(entity.get(attribute_key, "") for attribute_key in ("name", "description"))
        return set(re.findall(cls.TEST_CASE_KEY_RE, text_attributes))

    def test_results_to_count(self, source: SourceMeasurement) -> list[str]:
        """Return the test results to count for the source."""
        return [status.lower() for status in cast(list[str], self._parameters[source.source_uuid].get("test_result"))]
