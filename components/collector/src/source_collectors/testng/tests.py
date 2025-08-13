"""TestNG tests collector."""

from typing import ClassVar, cast
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceMeasurement, SourceResponses


class TestNGTests(XMLFileSourceCollector):
    """Collector for TestNG tests."""

    # Test status to test result mapping
    TEST_RESULT: ClassVar[dict[str, str]] = {"FAIL": "failed", "PASS": "passed", "SKIP": "skipped"}  # nosec

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the tests for the TestNG XML."""
        test_results_to_count = [status.lower() for status in cast(list[str], self._parameter("test_result"))]
        test_count = 0
        total = 0
        entities = Entities()
        for response in responses:
            tree = await parse_source_response_xml(response)
            for test_result in test_results_to_count:
                test_count += int(tree.get(test_result) or "0")
            total += int(tree.get("total") or "0")
            entities.extend(self.__entities(tree, test_results_to_count))
        return SourceMeasurement(value=str(test_count), total=str(total), entities=entities)

    @classmethod
    def __entities(cls, tree: Element, test_results_to_count: list[str]) -> Entities:
        """Transform the test methods into entities."""
        # Unfortunately, there's no DTD or XSD for the testng-result.xml format (see
        # https://github.com/testng-team/testng/issues/2371), so we have to make some assumptions about elements and
        # attributes here. We use element.attribute[key] to access attributes that we assume are mandatory so that we
        # get attribute errors if the assumption proves to be wrong. Note: the base source collector class will catch
        # these attribute errors, if any, and make them visible in the UI as measurements with parse errors.
        entities = Entities()
        parent_map = cls.parent_map(tree)
        for test_class in tree.findall(".//class"):
            class_name = test_class.attrib["name"]
            for test_method in test_class.findall(".//test-method"):
                test_result = cls.TEST_RESULT[test_method.attrib["status"].upper()]
                if test_method.get("is-config", "false") == "true" or test_result not in test_results_to_count:
                    continue  # Skip config (beforeClass/afterClass) methods and test results the user wants to ignore
                name = test_method.attrib["name"]
                description = test_method.get("description", "")  # Description is optional
                key = f"{class_name}_{name}"
                suite_names = cls.parent_names(test_method, parent_map)
                entities.append(
                    Entity(
                        key=key,
                        name=name,
                        description=description,
                        class_name=class_name,
                        test_result=test_result,
                        suite_names=suite_names,
                    ),
                )
        return entities
