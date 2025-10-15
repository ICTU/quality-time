"""JUnit test suites collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceMeasurement, SourceResponses

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type


class JUnitTestSuites(XMLFileSourceCollector):
    """Collector for JUnit test suites."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the test suites from the JUnit XML."""
        entities = Entities()
        total = 0
        for response in responses:
            tree = await parse_source_response_xml(response)
            if tree.tag == "testsuite" and len(tree.findall("testsuite")) == 0:
                test_suites = [tree]
            else:
                test_suites = tree.findall(".//testsuite[testcase]")
            for test_suite in test_suites:
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
        """Transform a test case into a test suite entity."""
        suite_name = suite.get("name", "unknown")
        tests = len(suite.findall("testcase"))
        skipped = int(suite.get("skipped", 0))
        failed = int(suite.get("failures", 0))
        errored = int(suite.get("errors", 0))
        passed = tests - (errored + failed + skipped)
        return Entity(
            key=suite.get("id") or suite_name,
            suite_name=suite_name,
            suite_result=cls.__suite_result(errored, failed, skipped),
            tests=str(tests),
            passed=str(passed),
            errored=str(errored),
            failed=str(failed),
            skipped=str(skipped),
        )

    @staticmethod
    def __suite_result(errored: int, failed: int, skipped: int) -> str:
        """Return the result of a test suite."""
        if errored:
            return "errored"
        if failed:
            return "failed"
        if skipped:
            return "skipped"
        return "passed"
