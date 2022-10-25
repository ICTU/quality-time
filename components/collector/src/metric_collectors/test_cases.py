"""Test cases collector."""

import logging
import re
from typing import cast, Sequence

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
    UNIFORMIZED_TEST_RESULTS = {"fail": "failed", "pass": "passed", "skip": "skipped"}
    # Regular expression to identify test case ids in test names and descriptions:
    TEST_CASE_KEY_RE = re.compile(r"\w+\-\d+")
    # The supported source types for test cases and test reports:
    TEST_CASE_SOURCE_TYPES = ["jira"]
    TEST_REPORT_SOURCE_TYPES = ["jenkins_test_report", "junit", "robot_framework", "testng"]

    async def collect(self) -> MetricMeasurement | None:
        """Override to add the test results from the test report(s) to the test cases."""
        logging.info("Debug TestCases #4663: collect()ing...")
        if (measurement := await super().collect()) is None:
            logging.info("Debug TestCases #4663: super().collect() returned no measurement")
            return None
        logging.info("Debug TestCases #4663: super().collect() returned a measurement: %s", measurement.as_dict())
        test_cases = self.test_cases(measurement.sources)
        test_case_keys = set(test_cases.keys())
        logging.info("Debug TestCases #4663: measurement has %d test cases: %s", len(test_case_keys), test_case_keys)
        # Derive the test result of the test cases from the test results of the tests
        logging.info("Debug TestCases #4663: processing test report entities...")
        for entity in self.test_report_entities(measurement.sources):
            logging.info("Debug TestCases #4663: processing test report entity %s...", entity["key"])
            logging.info(
                "Debug TestCases #4663: test cases referenced by the entity are %s", self.referenced_test_cases(entity)
            )
            for test_case_key in self.referenced_test_cases(entity) & test_case_keys:
                test_result_so_far = test_cases[test_case_key]["test_result"]
                test_result = self.test_result(entity)
                test_cases[test_case_key]["test_result"] = self.TEST_RESULT_STATE[(test_result_so_far, test_result)]
                logging.info(
                    "Debug TestCases #4663: test case %s test result is now %s",
                    test_case_key,
                    test_cases[test_case_key]["test_result"],
                )
            logging.info("Debug TestCases #4663: ...done processing test report entity %s", entity["key"])
        logging.info("Debug TestCases #4663: ...done processing test report entities")
        # Set the value of the test report sources to zero as this metric only counts test cases
        logging.info("Debug TestCases #4663: processing measurement sources...")
        for source in self.test_report_sources(measurement.sources):
            logging.info("Debug TestCases #4663: setting source.value to zero for source %s", source.source_uuid)
            source.value = "0"
        logging.info("Debug TestCases #4663: ...done processing measurement sources")
        # Filter the test cases by test result
        logging.info("Debug TestCases #4663: filtering the test cases by test result...")
        for source in self.test_case_sources(measurement.sources):
            source.entities = Entities(
                entity for entity in source.entities if entity["test_result"] in self.test_results_to_count(source)
            )
            source.value = str(len(source.entities))
            logging.info(
                "Debug TestCases #4663: setting source.value to %d for source %s", source.value, source.source_uuid
            )
        logging.info("Debug TestCases #4663: ...done filtering the test cases by test result")
        logging.info("Debug TestCases #4663: ...done collect()ing")
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
        return [source for source in sources if self.source_type(source) in self.TEST_CASE_SOURCE_TYPES]

    def test_report_entities(self, sources: Sequence[SourceMeasurement]) -> list[Entity]:
        """Return the test entities."""
        return [entity for source in self.test_report_sources(sources) for entity in source.entities]

    def test_report_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the test report sources."""
        return [source for source in sources if self.source_type(source) in self.TEST_REPORT_SOURCE_TYPES]

    @classmethod
    def referenced_test_cases(cls, entity: Entity) -> set[str]:
        """Return the keys of test cases referenced in test entity names or descriptions."""
        text_attributes = " ".join(entity.get(attribute_key, "") for attribute_key in ("name", "description"))
        return set(re.findall(cls.TEST_CASE_KEY_RE, text_attributes))

    def test_results_to_count(self, source: SourceMeasurement) -> list[str]:
        """Return the test results to count for the source."""
        return [status.lower() for status in cast(list[str], self._parameters[source.source_uuid].get("test_result"))]

    def source_type(self, source: SourceMeasurement) -> str:
        """Return the source type."""
        return str(self._metric["sources"][source.source_uuid]["type"])

    @classmethod
    def test_result(cls, entity: Entity) -> str:
        """Return the (uniformized) test result of the entity."""
        return cls.UNIFORMIZED_TEST_RESULTS.get(entity["test_result"], entity["test_result"])
