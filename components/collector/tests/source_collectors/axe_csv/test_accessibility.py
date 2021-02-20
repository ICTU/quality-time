"""Unit tests for the Axe accessibility collectors."""

from collector_utilities.functions import md5_hash

from ..source_collector_test_case import SourceCollectorTestCase


class AxeCSVAccessibilityTest(SourceCollectorTestCase):
    """Unit tests for the Axe CSV collector for accessibility violations."""

    SOURCE_TYPE = "axecsv"
    METRIC_TYPE = "accessibility"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.header_row = "URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element\n"
        self.serious_violation = "url1,aria-input-field-name,serious,help1,html1\n"
        self.moderate_violation = "url2,aria-hidden-focus,moderate,help2,html2,messages2,dom2\n"
        self.csv = self.header_row + self.serious_violation + self.moderate_violation
        self.expected_entities = [
            {
                "url": "url1",
                "violation_type": "aria-input-field-name",
                "impact": "serious",
                "element": None,
                "page": "url1",
                "description": None,
                "help": "help1",
            },
            {
                "url": "url2",
                "violation_type": "aria-hidden-focus",
                "impact": "moderate",
                "element": "dom2",
                "page": "url2",
                "description": "messages2",
                "help": "help2",
            },
        ]
        for entity in self.expected_entities:
            entity["key"] = md5_hash(",".join(str(value) for value in entity.values()))

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(self.metric, get_request_text=self.csv)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_no_issues(self):
        """Test zero issues."""
        response = await self.collect(self.metric, get_request_text="")
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.metric["sources"]["source_id"]["parameters"]["impact"] = ["serious", "critical"]
        response = await self.collect(self.metric, get_request_text=self.csv)
        self.assert_measurement(response, value="1")

    async def test_filter_by_violation_type(self):
        """Test that violations can be filtered by violation type."""
        self.metric["sources"]["source_id"]["parameters"]["violation_type"] = [
            "aria-input-field-name",
            "area-hidden-focus",
        ]
        response = await self.collect(self.metric, get_request_text=self.csv)
        self.assert_measurement(response, value="1")

    async def test_zipped_csv(self):
        """Test that a zip archive with CSV files is processed correctly."""
        self.metric["sources"]["source_id"]["parameters"]["url"] = "https://axecsv.zip"
        zipfile = self.zipped_report(*[(f"axe{index}.csv", self.csv) for index in range(2)])
        response = await self.collect(self.metric, get_request_content=zipfile)
        self.assert_measurement(response, value="4", entities=self.expected_entities + self.expected_entities)

    async def test_empty_line(self):
        """Test that empty lines are ignored."""
        response = await self.collect(self.metric, get_request_text=self.csv + "\n\n")
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_embedded_newlines(self):
        """Test that embedded newlines are ignored."""
        violation_with_newline = 'url3,aria-hidden-focus,moderate,help3,html3,"messages3\nsecond line",dom3\n'
        expected_entity = {
            "url": "url3",
            "violation_type": "aria-hidden-focus",
            "impact": "moderate",
            "element": "dom3",
            "page": "url3",
            "description": "messages3\nsecond line",
            "help": "help3",
        }
        expected_entity["key"] = md5_hash(",".join(str(value) for value in expected_entity.values()))
        response = await self.collect(self.metric, get_request_text=self.csv + violation_with_newline)
        self.assert_measurement(response, value="3", entities=self.expected_entities + [expected_entity])
