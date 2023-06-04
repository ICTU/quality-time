"""Unit tests for the cloc LOC collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ClocLOCTest(SourceCollectorTestCase):
    """Unit tests for the cloc LOC collector."""

    SOURCE_TYPE = "cloc"
    METRIC_TYPE = "loc"

    def setUp(self):
        """Extend to set up test fixtures."""
        super().setUp()
        self.cloc_json = {
            "header": {},
            "SUM": {},
            "Python": {"nFiles": 1, "blank": 5, "comment": 10, "code": 60},
            "JavaScript": {"nFiles": 1, "blank": 2, "comment": 0, "code": 30},
        }
        self.cloc_by_file_json = {
            "header": {},
            "SUM": {},
            "test_file": {"blank": 5, "comment": 10, "code": 60, "language": "Python"},
            "production_file": {"blank": 2, "comment": 0, "code": 30, "language": "JavaScript"},
        }
        self.expected_entities = [
            {"key": "Python", "language": "Python", "nr_files": "1", "blank": "5", "comment": "10", "code": "60"},
            {
                "key": "JavaScript",
                "language": "JavaScript",
                "nr_files": "1",
                "blank": "2",
                "comment": "0",
                "code": "30",
            },
        ]

    async def test_loc(self):
        """Test that the number of lines is returned and that the languages are returned as entities."""
        response = await self.collect(get_request_json_return_value=self.cloc_json)
        self.assert_measurement(response, value="90", total="90", entities=self.expected_entities)

    async def test_loc_ignore_languages(self):
        """Test that languages can be ignored."""
        self.set_source_parameter("languages_to_ignore", ["Java.*"])
        response = await self.collect(get_request_json_return_value=self.cloc_json)
        self.assert_measurement(response, value="60", total="60", entities=self.expected_entities[:1])

    async def test_loc_by_file(self):
        """Test that the number of lines is returned and that the languages are returned as entities."""
        response = await self.collect(get_request_json_return_value=self.cloc_by_file_json)
        self.assert_measurement(response, value="90", total="90", entities=self.expected_entities)

    async def test_loc_by_file_include_files(self):
        """Test that the number of lines is returned and that the languages are returned as entities."""
        self.set_source_parameter("files_to_include", ["test.*"])
        response = await self.collect(get_request_json_return_value=self.cloc_by_file_json)
        self.assert_measurement(response, value="60", total="90", entities=self.expected_entities[:1])
