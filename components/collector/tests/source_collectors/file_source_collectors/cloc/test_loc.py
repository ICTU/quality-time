"""Unit tests for the cloc LOC collector."""

from ...source_collector_test_case import SourceCollectorTestCase


class ClocLOCTest(SourceCollectorTestCase):
    """Unit tests for the cloc LOC collector."""

    SOURCE_TYPE = "cloc"
    METRIC_TYPE = "loc"

    def setUp(self):
        """Extend to set up test fixtures."""
        super().setUp()
        self.cloc_json = {
            "header": {},
            "SUM": {},  # header and SUM are not used
            "Python": {"nFiles": 1, "blank": 5, "comment": 10, "code": 60},
            "JavaScript": {"nFiles": 1, "blank": 2, "comment": 0, "code": 30},
        }
        self.expected_entities = [
            dict(key="Python", language="Python", nr_files="1", blank="5", comment="10", code="60")
        ]

    async def test_loc(self):
        """Test that the number of lines is returned and that the languages are returned as entities."""
        self.expected_entities.append(
            dict(key="JavaScript", language="JavaScript", nr_files="1", blank="2", comment="0", code="30")
        )
        response = await self.collect(self.metric, get_request_json_return_value=self.cloc_json)
        self.assert_measurement(response, value="90", total="100", entities=self.expected_entities)

    async def test_loc_ignore_languages(self):
        """Test that languages can be ignored."""
        self.sources["source_id"]["parameters"]["languages_to_ignore"] = ["Java.*"]
        response = await self.collect(self.metric, get_request_json_return_value=self.cloc_json)
        self.assert_measurement(response, value="60", total="100", entities=self.expected_entities)
