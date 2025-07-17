"""Robot Framework test suites collector."""

from typing import TYPE_CHECKING, cast

from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import RobotFrameworkBaseClass

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

    from collector_utilities.type import Response


class RobotFrameworkTestSuites(RobotFrameworkBaseClass):
    """Collector for Robot Framework test suites."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests from the Robot Framework XML."""
        nr_of_suites, total_nr_of_suites, suite_entities = 0, 0, Entities()
        test_results = cast(list[str], self._parameter("test_result"))
        for response in responses:
            count, total, entities = await self._parse_source_response(response, test_results)
            nr_of_suites += count
            total_nr_of_suites += total
            suite_entities.extend(entities)
        return SourceMeasurement(value=str(nr_of_suites), total=str(total_nr_of_suites), entities=suite_entities)

    @classmethod
    async def _parse_source_response(cls, response: Response, test_results: list[str]) -> tuple[int, int, Entities]:
        """Parse a Robot Framework XML."""
        nr_of_suites, total_nr_of_suites, entities = 0, 0, Entities()
        tree = await parse_source_response_xml(response)
        for suite in tree.findall(".//suite[test]"):
            total_nr_of_suites += 1
            suite_status = suite.find("status")
            if suite_status is None:
                continue
            suite_result = suite_status.get("status", "").lower()
            if suite_result not in test_results:
                continue
            nr_of_suites += 1
            entities.append(cls._create_entity(suite, suite_result))
        return nr_of_suites, total_nr_of_suites, entities

    @classmethod
    def _create_entity(cls, suite: Element, suite_result: str) -> Entity:
        """Create a measurement entity from the test suite element."""
        suite_id = suite.get("id", "")
        suite_name = suite.get("name", "unknown")
        doc = suite.find("doc")
        suite_documentation = "" if doc is None else doc.text
        tests = len(suite.findall("test"))
        failed = cls._nr_tests(suite, "FAIL")
        errored = cls._nr_tests(suite, "ERROR")
        skipped = cls._nr_tests(suite, "SKIP")
        passed = tests - (failed + errored + skipped)
        return Entity(
            key=suite_id,
            suite_name=suite_name,
            suite_documentation=suite_documentation,
            suite_result=suite_result,
            tests=str(tests),
            passed=str(passed),
            failed=str(failed),
            errored=str(errored),
            skipped=str(skipped),
        )

    @staticmethod
    def _nr_tests(suite: Element, status: str) -> int:
        """Return the number of tests in the suite with the given status."""
        return len(suite.findall(f"test/status[@status='{status}']"))
