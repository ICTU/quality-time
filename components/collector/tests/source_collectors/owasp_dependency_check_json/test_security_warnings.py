"""Unit tests for the OWASP Dependency-Check JSON security warnings collector."""

from .base import OWASPDependencyCheckJSONTestCase


class OWASPDependencyCheckJSONSecurityWarningsTest(OWASPDependencyCheckJSONTestCase):
    """Unit tests for the OWASP Dependency-Check JSON security warnings collector."""

    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test that the number of warnings is returned."""
        response = await self.collect(get_request_json_return_value=self.json)
        expected_entities = [
            {
                "key": "12345",
                "url": "https://owasp_dependency_check_json#l1_12345",
                "highest_severity": "Medium",
                "nr_vulnerabilities": "2",
                "file_name": self.file_name,
                "file_path": self.file_path,
                "file_path_after_regexp": self.file_path,
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_low_warnings(self):
        """Test that the number of warnings is returned."""
        self.json["dependencies"] = [
            {
                "isVirtual": False,
                "sha1": "12345",
                "fileName": f"{self.file_name}",
                "filePath": f"{self.file_path}",
                "vulnerabilities": [{"severity": "LOW"}],
            }
        ]
        response = await self.collect(get_request_json_return_value=self.json)
        expected_entities = [
            {
                "key": "12345",
                "url": "https://owasp_dependency_check_json#l1_12345",
                "highest_severity": "Low",
                "nr_vulnerabilities": "1",
                "file_name": self.file_name,
                "file_path": self.file_path,
                "file_path_after_regexp": self.file_path,
            },
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_multiple_warnings_with_same_filepath(self):
        """Test that the hashes are based on both the file path and the file name."""
        self.json["dependencies"] = [
            {
                "isVirtual": False,
                "fileName": "CuttingEdge.Conditions:1.2.0.0",
                "filePath": "packages.config",
                "vulnerabilities": [{"severity": "LOW"}],
            },
            {
                "isVirtual": False,
                "fileName": "IdentityModel:1.13.1",
                "filePath": "packages.config",
                "vulnerabilities": [{"severity": "LOW"}],
            },
        ]
        response = await self.collect(get_request_json_return_value=self.json)
        expected_file_path = "packages.config"
        expected_entities = [
            {
                "key": "498ac4bf0c766490ad58cd04a71e07a439b97fc8",
                "url": "",
                "file_name": "CuttingEdge.Conditions:1.2.0.0",
                "highest_severity": "Low",
                "nr_vulnerabilities": "1",
                "file_path": expected_file_path,
                "file_path_after_regexp": expected_file_path,
            },
            {
                "key": "7f5f471406d316dfeb580de2738db563f3c7ac97",
                "url": "",
                "file_name": "IdentityModel:1.13.1",
                "highest_severity": "Low",
                "nr_vulnerabilities": "1",
                "file_path": expected_file_path,
                "file_path_after_regexp": expected_file_path,
            },
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)
