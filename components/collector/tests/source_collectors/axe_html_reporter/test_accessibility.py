"""Unit tests for the Axe HTML reporter accessibility collector."""

import pathlib

from collector_utilities.functions import md5_hash
from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AxeHTMLAccessibilityTest(SourceCollectorTestCase):
    """Unit tests for the Axe HTML reporter collector for accessibility violations."""

    METRIC_TYPE = "accessibility"
    SOURCE_TYPE = "axe_html_reporter"

    expected_entities: list[dict[str, str]]

    @classmethod
    def setUpClass(cls) -> None:
        """Extend to read the Axe HTML report and set the expected entities."""
        super().setUpClass()
        axe_html_report = (
            pathlib.Path(__file__).parent.parent.parent.parent.parent / "testdata/reports/axe/axe-html-reporter.html"
        )
        cls.html = axe_html_report.read_text()
        cls.expected_entities = [
            {
                "element": "<html>",
                "violation_type": "html-has-lang",
                "description": "Ensures every HTML document has a lang attribute",
                "tags": "cat.language, wcag2a, wcag311",
                "impact": "serious",
            },
            {
                "element": "<html>",
                "violation_type": "landmark-one-main",
                "description": "Ensures the document has a main landmark",
                "tags": "best-practice, cat.semantics",
                "impact": "moderate",
            },
            {
                "element": "<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples "
                "in documents. You may use this\n    domain in literature without prior coordination or asking "
                'for permission.</p>\n    <p><a href="https://www.iana.org/domains/example">More '
                "information...</a></p>\n</div>",
                "violation_type": "region",
                "description": "Ensures all page content is contained by landmarks",
                "tags": "best-practice, cat.keyboard",
                "impact": "moderate",
            },
            {
                "element": '<input type="text" value="" class="city-input ac_input ui-autocomplete-input" '
                'autocomplete="off" id="from0" name="from0" tabindex="1" role="textbox" '
                'aria-autocomplete="list" aria-haspopup="true">',
                "violation_type": "tabindex",
            },
            {
                "element": '<input type="text" value="" class="city-input ac_input ui-autocomplete-input" '
                'autocomplete="off" id="to0" name="to0" tabindex="1" role="textbox" aria-autocomplete="list" '
                'aria-haspopup="true">',
                "violation_type": "tabindex",
            },
            {
                "element": '<input size="10" id="deptDate0" name="deptDate0" placeholder="mm/dd/yyyy" value="" '
                'tabindex="3" class="hasDatepicker input-dept">',
                "violation_type": "tabindex",
            },
        ]
        for entity in cls.expected_entities:
            entity["page"] = entity["url"] = "https://example.com/"
            entity["help"] = f"https://dequeuniversity.com/rules/axe/3.5/{entity['violation_type']}?application=axeAPI"
            entity["result_type"] = "violations"
            if entity["violation_type"] == "tabindex":
                entity["description"] = "Ensures tabindex attribute values are not greater than 0"
                entity["tags"] = "best-practice, cat.keyboard"
                entity["impact"] = "serious"
            entity["key"] = md5_hash(",".join(sorted(entity.values())))

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="6", entities=self.expected_entities)

    async def test_no_issues(self):
        """Test zero issues."""
        self.html = (
            '<div class="summary"><a href="https:&#x2F;&#x2F;example.com&#x2F;">'
            "https:&#x2F;&#x2F;example.com&#x2F</a></div>"
        )
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.set_source_parameter("impact", ["serious", "critical"])
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="4")

    async def test_filter_by_tag_include(self):
        """Test that violations can be filtered by tag."""
        self.set_source_parameter("tags_to_include", ["wcag2a"])
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[0]])

    async def test_filter_by_tag_ignore(self):
        """Test that violations can be filtered by tag."""
        self.set_source_parameter("tags_to_ignore", ["best-practice"])
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[0]])

    async def test_zipped_hrml(self):
        """Test that a zip archive with HTML files is processed correctly."""
        self.set_source_parameter("url", "axe.zip")
        zipfile = self.zipped_report(*[(f"axe{index}.html", self.html) for index in range(2)])
        response = await self.collect(get_request_content=zipfile)
        self.assert_measurement(response, value="6", entities=self.expected_entities)  # Duplicates are discarded

    async def test_passed_rules(self):
        """Test that passed rules can be counted as well."""
        self.set_source_parameter("result_types", ["passes"])
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="12")

    async def test_inapplicable_rules(self):
        """Test that inapplicable rules can be counted as well."""
        self.set_source_parameter("result_types", ["inapplicable"])
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="68")

    async def test_incomplete_rules(self):
        """Test that incomplete rules can be counted as well."""
        self.set_source_parameter("result_types", ["incomplete"])
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="0")
