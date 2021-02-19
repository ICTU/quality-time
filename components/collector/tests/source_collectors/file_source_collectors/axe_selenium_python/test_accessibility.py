"""Unit tests for the Axe report generated by axe-selenium-python accessibility collector."""

import io
import json
import zipfile

from collector_utilities.functions import md5_hash

from .base import AxeSeleniumPythonTestCase


class AxeSeleniumPythonAccessibilityTest(AxeSeleniumPythonTestCase):
    """Unit tests for the axe-selenium-python collector for accessibility violations."""

    METRIC_TYPE = "accessibility"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.tested_url = "https://tested_url"
        self.json = dict(
            url=self.tested_url,
            violations=[
                dict(
                    id="aria-input-field-name",
                    description="description1",
                    helpUrl="https://help1",
                    tags=["cat.color", "wcag2aa", "wcag143"],
                    nodes=[dict(impact="serious", html="html1")],
                ),
                dict(
                    id="aria-hidden-focus",
                    description="description2",
                    helpUrl="https://help2",
                    nodes=[dict(impact="moderate", html="html2")],
                ),
            ],
        )
        self.expected_entities = [
            {
                "description": "description1",
                "element": "html1",
                "help": "https://help1",
                "impact": "serious",
                "page": self.tested_url,
                "url": self.tested_url,
                "violation_type": "aria-input-field-name",
                "tags": "cat.color, wcag143, wcag2aa",
            },
            {
                "description": "description2",
                "element": "html2",
                "help": "https://help2",
                "impact": "moderate",
                "page": self.tested_url,
                "url": self.tested_url,
                "violation_type": "aria-hidden-focus",
                "tags": "",
            },
        ]
        for entity in self.expected_entities:
            entity["key"] = md5_hash(",".join(str(value) for key, value in entity.items() if key != "tags"))

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.json)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_no_issues(self):
        """Test zero issues."""
        self.json["violations"] = []
        response = await self.collect(self.metric, get_request_json_return_value=self.json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.sources["source_id"]["parameters"]["impact"] = ["serious", "critical"]
        response = await self.collect(self.metric, get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1")

    async def test_filter_by_tag_include(self):
        """Test that violations can be filtered by tag."""
        self.sources["source_id"]["parameters"]["tags_to_include"] = ["wcag2aa"]
        response = await self.collect(self.metric, get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[0]])

    async def test_filter_by_tag_ignore(self):
        """Test that violations can be filtered by tag."""
        self.sources["source_id"]["parameters"]["tags_to_ignore"] = ["wcag2aa"]
        response = await self.collect(self.metric, get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[1]])

    async def test_zipped_json(self):
        """Test that a zip archive with JSON files is processed correctly."""
        self.sources["source_id"]["parameters"]["url"] = "axe.zip"
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_axe_json:
            for index in range(2):
                zipped_axe_json.writestr(f"axe{index}.json", json.dumps(self.json))
        response = await self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="4", entities=self.expected_entities + self.expected_entities)
