"""Unit tests for the Axe HTML reporter accessibility collector."""

import pathlib

from collector_utilities.functions import md5_hash

from ..source_collector_test_case import SourceCollectorTestCase


class AxeHTMLAccessibilityTest(SourceCollectorTestCase):
    """Unit tests for the Axe HTML reporter collector for accessibility violations."""

    METRIC_TYPE = "accessibility"
    SOURCE_TYPE = "axe_html_reporter"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        axe_html_report = (
            pathlib.Path(__file__).parent.parent.parent.parent.parent / "testdata/reports/axe/axe-html-reporter.html"
        )
        self.html = axe_html_report.read_text()
        self.expected_entities = [
            dict(
                element="<html>",
                violation_type="html-has-lang",
                description="Ensures every HTML document has a lang attribute",
                tags="cat.language, wcag2a, wcag311",
                impact="serious",
                help="https://dequeuniversity.com/rules/axe/3.5/html-has-lang?application=axeAPI",
            ),
            dict(
                element="<html>",
                violation_type="landmark-one-main",
                description="Ensures the document has a main landmark",
                tags="best-practice, cat.semantics",
                impact="moderate",
                help="https://dequeuniversity.com/rules/axe/3.5/landmark-one-main?application=axeAPI",
            ),
            dict(
                element="""<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href="https://www.iana.org/domains/example">More information...</a></p>\n</div>""",
                violation_type="region",
                description="Ensures all page content is contained by landmarks",
                tags="best-practice, cat.keyboard",
                impact="moderate",
                help="https://dequeuniversity.com/rules/axe/3.5/region?application=axeAPI",
            ),
            dict(
                element="""<input type="text" value="" class="city-input ac_input ui-autocomplete-input" autocomplete="off" id="from0" name="from0" tabindex="1" role="textbox" aria-autocomplete="list" aria-haspopup="true">""",
                violation_type="tabindex",
                description="Ensures tabindex attribute values are not greater than 0",
                tags="best-practice, cat.keyboard",
                impact="serious",
                help="https://dequeuniversity.com/rules/axe/3.5/tabindex?application=axeAPI",
            ),
            dict(
                element="""<input type="text" value="" class="city-input ac_input ui-autocomplete-input" autocomplete="off" id="to0" name="to0" tabindex="1" role="textbox" aria-autocomplete="list" aria-haspopup="true">""",
                violation_type="tabindex",
                description="Ensures tabindex attribute values are not greater than 0",
                tags="best-practice, cat.keyboard",
                impact="serious",
                help="https://dequeuniversity.com/rules/axe/3.5/tabindex?application=axeAPI",
            ),
            dict(
                element="""<input size="10" id="deptDate0" name="deptDate0" placeholder="mm/dd/yyyy" value="" tabindex="3" class="hasDatepicker input-dept">""",
                violation_type="tabindex",
                description="Ensures tabindex attribute values are not greater than 0",
                tags="best-practice, cat.keyboard",
                impact="serious",
                help="https://dequeuniversity.com/rules/axe/3.5/tabindex?application=axeAPI",
            ),
        ]
        for entity in self.expected_entities:
            entity["page"] = entity["url"] = "http://example.com/"
            entity["key"] = md5_hash(",".join(sorted(entity.values())))

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="6", entities=self.expected_entities)

    async def test_no_issues(self):
        """Test zero issues."""
        self.html = """<div class="summary"><a href="http:&#x2F;&#x2F;example.com&#x2F;">http:&#x2F;&#x2F;example.com&#x2F</a></div>"""
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="0", entities=[])

    '''
    async def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.set_source_parameter("impact", ["serious", "critical"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1")

    async def test_filter_by_tag_include(self):
        """Test that violations can be filtered by tag."""
        self.set_source_parameter("tags_to_include", ["wcag2aa"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[0]])

    async def test_filter_by_tag_ignore(self):
        """Test that violations can be filtered by tag."""
        self.set_source_parameter("tags_to_ignore", ["wcag2aa"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[1]])

    async def test_zipped_json(self):
        """Test that a zip archive with JSON files is processed correctly."""
        self.set_source_parameter("url", "axe.zip")
        zipfile = self.zipped_report(*[(f"axe{index}.json", json.dumps(self.json)) for index in range(2)])
        response = await self.collect(get_request_content=zipfile)
        self.assert_measurement(response, value="2", entities=self.expected_entities)  # Duplicates are discarded

    async def test_json_with_only_violations(self):
        """Test that a JSON file with just a list of violations works."""
        for entity in self.expected_entities:
            entity["page"] = ""
            entity["url"] = ""
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=self.json["violations"])
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_json_with_nested_lists_with_only_violations(self):
        """Test that a JSON file with a nested list of violations works."""
        for entity in self.expected_entities:
            entity["page"] = ""
            entity["url"] = ""
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=[self.json["violations"]])
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_json_with_list_of_result_type_dicts(self):
        """Test that a JSON file with a list of result type dicts works."""
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=[self.json])
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_result_type_parameter(self):
        """Test that other result types besides violations can be counted as well."""
        self.set_source_parameter("result_types", ["violations", "passes"])
        self.expected_entities.append(
            dict(
                description="Ensures aria-hidden='true' is not present on the document body.",
                element="<body>",
                help="https://dequeuniversity.com/rules/axe/4.1/aria-hidden-body?application=axeAPI",
                impact=None,
                page=self.tested_url,
                url=self.tested_url,
                result_type="passes",
                tags="cat.aria, wcag2a, wcag412",
                violation_type="aria-hidden-body",
            )
        )
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="3", entities=self.expected_entities)

    async def test_result_type_without_nodes(self):
        """Test that result types without nodes can be counted as well."""
        self.set_source_parameter("result_types", ["violations", "inapplicable"])
        self.expected_entities.append(
            dict(
                description="Ensures ARIA attributes are allowed for an element's role",
                element=None,
                help="https://dequeuniversity.com/rules/axe/4.1/aria-allowed-attr?application=axeAPI",
                impact=None,
                page=self.tested_url,
                url=self.tested_url,
                result_type="inapplicable",
                tags="cat.aria, wcag2a, wcag412",
                violation_type="aria-allowed-attr",
            )
        )
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="3", entities=self.expected_entities)
    '''
