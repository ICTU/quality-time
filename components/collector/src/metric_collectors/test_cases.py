"""Test cases collector."""

import re
from collections.abc import Sequence
from typing import ClassVar, Literal, cast

from base_collectors import MetricCollector
from model import Entities, Entity, MetricMeasurement, SourceMeasurement

TestResult = Literal["untested", "passed", "skipped", "failed", "errored"]


class TestCases(MetricCollector):
    """Test cases collector."""

    __test__ = False  # Tell nose that this is not a test class

    # Mapping to calculate the test result of a test case. The keys are tuples of the current test result of the test
    # case and the next test result found. The value is the resulting test result. For example,
    # {("passed", "skipped"), "skipped"} means that if a test case has passed so far and we see a skipped test result,
    # the updated test result state of the test case is skipped.
    TEST_RESULT_STATE: ClassVar[dict[tuple[TestResult, TestResult], TestResult]] = {
        ("untested", "passed"): "passed",
        ("untested", "skipped"): "skipped",
        ("untested", "failed"): "failed",
        ("untested", "errored"): "errored",
        ("passed", "passed"): "passed",
        ("passed", "skipped"): "skipped",
        ("passed", "failed"): "failed",
        ("passed", "errored"): "errored",
        ("skipped", "passed"): "skipped",
        ("skipped", "skipped"): "skipped",
        ("skipped", "failed"): "failed",
        ("skipped", "errored"): "errored",
        ("failed", "passed"): "failed",
        ("failed", "skipped"): "failed",
        ("failed", "failed"): "failed",
        ("failed", "errored"): "errored",
        ("errored", "passed"): "errored",
        ("errored", "skipped"): "errored",
        ("errored", "failed"): "errored",
        ("errored", "errored"): "errored",
    }
    # Mapping to uniformize the test results from different sources:
    UNIFORMIZED_TEST_RESULTS: ClassVar[dict[str, TestResult]] = {
        "aborted": "errored",
        "completed": "passed",
        "disconnected": "errored",
        "error": "errored",
        "fail": "failed",
        "inconclusive": "skipped",
        "inprogress": "untested",
        "notexecuted": "skipped",
        "notrunnable": "skipped",
        "pass": "passed",
        "passedbutrunaborted": "passed",
        "pending": "untested",
        "skip": "skipped",
        "timeout": "errored",
        "warning": "errored",
    }
    # Regular expression to identify test case ids in entity attributes. Matches identifiers of the form BAR-123,
    # while ensuring they are not part of longer identifiers such as FOO-BAR-123 or BAR-123-456:
    TEST_CASE_KEY_RE = re.compile(r"(?<![-\w])\b[A-Za-z]+\-\d+\b(?![-\w])")
    ENTITY_ATTRIBUTES_TO_SEARCH = ("name", "test_name", "description", "suite_name", "suite_names")
    # The supported source types for test cases and test reports:
    TEST_CASE_SOURCE_TYPES: ClassVar[list[str]] = ["jira"]
    TEST_REPORT_SOURCE_TYPES: ClassVar[list[str]] = [
        "jenkins_test_report",
        "junit",
        "robot_framework",
        "testng",
        "visual_studio_trx",
    ]

    async def collect(self) -> MetricMeasurement | None:
        """Override to add the test results from the test report(s) to the test cases."""
        if (measurement := await super().collect()) is None:
            return None
        test_cases = self.test_cases(measurement.sources)
        test_case_keys = set(test_cases.keys())
        if not test_case_keys:
            for source in measurement.sources:
                source.parse_error = "No test case keys found in this source"
            return measurement
        # Derive the test result of the test cases from the test results of the tests
        for entity in self.test_report_entities(measurement.sources):
            for test_case_key in self.referenced_test_cases(entity) & test_case_keys:
                test_result_so_far = cast(TestResult, test_cases[test_case_key]["test_result"])
                test_result = self.test_result(entity)
                test_cases[test_case_key]["test_result"] = self.TEST_RESULT_STATE[(test_result_so_far, test_result)]
        # Set the value of the test report sources to zero as this metric only counts test cases
        for source in self.test_report_sources(measurement.sources):
            source.value = "0"
        # Filter the test cases by test result
        for source in self.test_case_sources(measurement.sources):
            entities = source.get_entities()
            source.entities = Entities(
                entity for entity in entities if entity["test_result"] in self.test_results_to_count(source)
            )
            source.value = str(len(source.entities))
        return measurement

    def test_cases(self, sources: Sequence[SourceMeasurement]) -> dict[str, Entity]:
        """Return the test cases, indexed by their keys, with test result initialized to untested."""
        test_cases = {
            entity["issue_key"]: entity
            for source in self.test_case_sources(sources)
            for entity in source.get_entities()
        }
        for entity in test_cases.values():
            entity.setdefault("test_result", "untested")
        return test_cases

    def test_case_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the test case sources."""
        return [source for source in sources if self.source_type(source) in self.TEST_CASE_SOURCE_TYPES]

    def test_report_entities(self, sources: Sequence[SourceMeasurement]) -> list[Entity]:
        """Return the test entities."""
        return [entity for source in self.test_report_sources(sources) for entity in source.get_entities()]

    def test_report_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the test report sources."""
        return [source for source in sources if self.source_type(source) in self.TEST_REPORT_SOURCE_TYPES]

    @classmethod
    def referenced_test_cases(cls, entity: Entity) -> set[str]:
        """Return the keys of test cases referenced in test entity names or descriptions."""
        text_attributes = " ".join(entity.get(attribute_key, "") for attribute_key in cls.ENTITY_ATTRIBUTES_TO_SEARCH)
        return set(re.findall(cls.TEST_CASE_KEY_RE, text_attributes))

    def test_results_to_count(self, source: SourceMeasurement) -> list[TestResult]:
        """Return the test results to count for the source."""
        return [cast(TestResult, result.lower()) for result in self._parameters[source.source_uuid].get("test_result")]

    def source_type(self, source: SourceMeasurement) -> str:
        """Return the source type."""
        return str(self._metric["sources"][source.source_uuid]["type"])

    @classmethod
    def test_result(cls, entity: Entity) -> TestResult:
        """Return the (uniformized) test result of the entity."""
        test_result = cast(TestResult, entity["test_result"].lower())
        return cls.UNIFORMIZED_TEST_RESULTS.get(test_result, test_result)
