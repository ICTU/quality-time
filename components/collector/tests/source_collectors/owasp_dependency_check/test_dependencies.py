"""Unit tests for the OWASP Dependency Check dependencies collector."""

from collector_utilities.functions import sha1_hash

from .base import OWASPDependencyCheckTestCase


class OWASPDependencyCheckDependenciesTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    METRIC_TYPE = "dependencies"

    async def test_dependencies(self):
        """Test that the dependencies are returned."""
        response = await self.collect(get_request_text=self.xml)
        expected_entities = [
            dict(
                key="12345",
                url="https://owasp_dependency_check#l1_12345",
                file_name=self.file_name,
                file_path=self.file_path,
                file_path_after_regexp=self.file_path,
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_ignore_part_of_file_path(self):
        """Test that parts of the file path can be ignored, if the secrity warning has no sha1."""
        self.set_source_parameter("variable_file_path_regexp", ["/home/[a-z]+/"])
        response = await self.collect(get_request_text=self.xml.replace("<sha1>12345</sha1>", ""))
        file_path_after_regexp = self.file_path[len("/home/jenkins/") :]
        expected_entities = [
            dict(
                key=sha1_hash(file_path_after_regexp + self.file_name),
                url="",
                file_name=self.file_name,
                file_path=self.file_path,
                file_path_after_regexp=file_path_after_regexp,
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
