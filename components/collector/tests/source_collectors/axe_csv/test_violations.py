"""Unit tests for the Axe accessibility collectors."""

from shared.utils.functions import md5_hash

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AxeCSVViolationsTest(SourceCollectorTestCase):
    """Unit tests for the Axe CSV collector for accessibility violations."""

    SOURCE_TYPE = "axecsv"
    METRIC_TYPE = "violations"

    def setUp(self) -> None:
        """Extend to set up test data."""
        super().setUp()
        self.header_row = "URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element\n"
        self.serious_violation = "url1,aria-input-field-name,serious,help1,html1\n"
        self.serious_violation2 = "url2,aria-input-field-name,serious,help1,html2\n"
        self.moderate_violation = "url2,aria-hidden-focus,moderate,help2,html2,messages2,dom2\n"
        self.csv = self.header_row + self.serious_violation + self.moderate_violation
        self.csv2 = self.header_row + self.serious_violation2 + self.moderate_violation
        self.expected_entities: list[dict] = [
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
            entity["key"] = self.entity_key(entity)

    @staticmethod
    def entity_key(entity: dict[str, str]) -> str:
        """Create the entity hash."""
        return md5_hash(",".join(str(value) for value in entity.values()))

    async def test_nr_of_violations(self):
        """Test that the number of violations is returned."""
        measurement = await self.collect_measurement(get_request_text=self.csv)
        self.assert_measurement(measurement, value="2", entities=self.expected_entities)

    async def test_duplicate_violations(self):
        """Test that duplicate violations are ignored."""
        self.csv += self.serious_violation
        measurement = await self.collect_measurement(get_request_text=self.csv)
        self.assert_measurement(measurement, value="2", entities=self.expected_entities)

    async def test_no_violations(self):
        """Test zero violations."""
        measurement = await self.collect_measurement(get_request_text="")
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.set_source_parameter("impact", ["serious", "critical"])
        measurement = await self.collect_measurement(get_request_text=self.csv)
        self.assert_measurement(measurement, value="1")

    async def test_element_include_filter(self):
        """Test that violations can be filtered by element."""
        self.set_source_parameter("element_include_filter", ["dom2"])
        measurement = await self.collect_measurement(get_request_text=self.csv)
        self.assert_measurement(measurement, value="1", entities=[self.expected_entities[1]])

    async def test_element_exclude_filter(self):
        """Test that violations can be filtered by element."""
        self.set_source_parameter("element_exclude_filter", ["dom2"])
        measurement = await self.collect_measurement(get_request_text=self.csv)
        self.assert_measurement(measurement, value="1", entities=[self.expected_entities[0]])

    async def test_zipped_csv(self) -> None:
        """Test that a zip archive with CSV files is processed correctly."""
        self.set_source_parameter("url", "https://example.org/axecsv.zip")
        zipfile = self.zipped_report(*[("axe1.csv", self.csv), ("axe2.csv", self.csv2)])
        measurement = await self.collect_measurement(get_request_content=zipfile)
        expected_entity: dict = {
            "url": "url2",
            "violation_type": "aria-input-field-name",
            "impact": "serious",
            "element": None,
            "page": "url2",
            "description": None,
            "help": "help1",
        }
        expected_entity["key"] = self.entity_key(expected_entity)
        self.assert_measurement(measurement, value="3", entities=[*self.expected_entities, expected_entity])

    async def test_empty_line(self):
        """Test that empty lines are ignored."""
        measurement = await self.collect_measurement(get_request_text=self.csv + "\n\n")
        self.assert_measurement(measurement, value="2", entities=self.expected_entities)

    async def test_variable_url_regexp(self) -> None:
        """Test that parts of URLs can be ignored."""
        self.set_source_parameter("variable_url_regexp", ["url1"])
        expected_entity: dict = {
            "url": "variable-part-removed",
            "violation_type": "aria-input-field-name",
            "impact": "serious",
            "element": None,
            "page": "variable-part-removed",
            "description": None,
            "help": "help1",
        }
        expected_entity["key"] = self.entity_key(expected_entity)
        measurement = await self.collect_measurement(get_request_text=self.csv)
        self.assert_measurement(measurement, value="2", entities=[expected_entity, self.expected_entities[1]])

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
        expected_entity["key"] = self.entity_key(expected_entity)
        measurement = await self.collect_measurement(get_request_text=self.csv + violation_with_newline)
        self.assert_measurement(measurement, value="3", entities=[*self.expected_entities, expected_entity])
