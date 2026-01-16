"""Unit tests for the OWASP Dependency-Check JSON dependencies collector."""

from unittest.mock import patch

from collector_utilities.functions import sha1_hash

from .base import OWASPDependencyCheckJSONTestCase

ALLOWED_SCHEMAS = (
    "source_collectors.owasp_dependency_check_json.base.OWASPDependencyCheckJSONBase.allowed_report_schemas"
)


class OWASPDependencyCheckDependenciesTest(OWASPDependencyCheckJSONTestCase):
    """Unit tests for the OWASP Dependency-Check dependency collector."""

    METRIC_TYPE = "dependencies"

    async def test_dependencies(self):
        """Test that the dependencies are returned."""
        response = await self.collect(get_request_json_return_value=self.json)
        expected_entities = [
            {
                "key": "12345",
                "url": "https://owasp_dependency_check_json#l1_12345",
                "file_name": self.file_name,
                "file_path": self.file_path,
                "file_path_after_regexp": self.file_path,
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_ignore_part_of_file_path(self):
        """Test that parts of the file path can be ignored, if the security warning has no sha1."""
        self.set_source_parameter("variable_file_path_regexp", ["/home/[a-z]+/"])
        del self.json["dependencies"][0]["sha1"]
        response = await self.collect(get_request_json_return_value=self.json)
        file_path_after_regexp = self.file_path[len("/home/jenkins/") :]
        expected_entities = [
            {
                "key": sha1_hash(file_path_after_regexp + self.file_name),
                "url": "",
                "file_name": self.file_name,
                "file_path": self.file_path,
                "file_path_after_regexp": file_path_after_regexp,
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    @patch(ALLOWED_SCHEMAS, ["1.1"])
    async def test_invalid_report_schema_when_one_is_valid(self):
        """Test that an invalid report schema version results in an error message."""
        json = {"reportSchema": "1.0"}
        response = await self.collect(get_request_json_return_value=json)
        expected_error = 'The value of the JSON attribute "reportSchema" should be equal to "1.1" but is "1.0"'
        self.assert_measurement(response, parse_error=expected_error)

    @patch(ALLOWED_SCHEMAS, ["1.1", "1.2"])
    async def test_invalid_report_schema_when_multiple_are_valid(self):
        """Test that an invalid report schema version results in an error message."""
        json = {"reportSchema": "1.0"}
        response = await self.collect(get_request_json_return_value=json)
        expected_error = 'The value of the JSON attribute "reportSchema" should be one of "1.1", "1.2" but is "1.0"'
        self.assert_measurement(response, parse_error=expected_error)
