"""TestNG test suites collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceMeasurement, SourceResponses

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type


class TestNGTestSuites(XMLFileSourceCollector):
    """Collector for TestNG test suites."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the suites for the TestNG XML."""
        entities = Entities()
        total = 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_suite in tree.findall(".//suite[test]"):
                parsed_entity = self.__entity(test_suite)
                if self._include_entity(parsed_entity):
                    entities.append(parsed_entity)
                total += 1
        return SourceMeasurement(entities=entities, total=str(total))

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        results_to_count = cast(list[str], self._parameter("test_result"))
        return entity["suite_result"] in results_to_count

    @classmethod
    def __entity(cls, suite: Element) -> Entity:
        """Transform a test suite element into a test suite entity."""
        name = suite.get("name", "unknown")
        tests = len(suite.findall(".//test-method"))
        skipped = cls._nr_tests(suite, "SKIP")
        failed = cls._nr_tests(suite, "FAIL")
        passed = cls._nr_tests(suite, "PASS")
        ignored = tests - (skipped + failed + passed)
        suite_result = "passed"
        if failed:
            suite_result = "failed"
        elif skipped:
            suite_result = "skipped"
        elif ignored:
            suite_result = "ignored"
        return Entity(
            key=name,
            suite_name=name,
            suite_result=suite_result,
            tests=str(tests),
            passed=str(passed),
            ignored=str(ignored),
            failed=str(failed),
            skipped=str(skipped),
        )

    @staticmethod
    def _nr_tests(suite: Element, status: str) -> int:
        """Return the number of tests in the suite with the given status."""
        return len(suite.findall(f".//test-method[@status='{status}']"))
