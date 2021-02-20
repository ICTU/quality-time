"""Unit tests for the OWASP Dependency Check security warnings collector."""

from .base import OWASPDependencyCheckTestCase

from source_collectors.file_source_collectors.owasp_dependency_check.dependencies import OWASPDependencyCheckBase


class OWASPDependencyCheckSecurityWarningsTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check security warnings collector."""

    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test that the number of warnings is returned."""
        response = await self.collect(self.metric, get_request_text=self.xml)
        expected_entities = [
            dict(
                key="12345",
                url="https://owasp_dependency_check#l1_12345",
                highest_severity="Medium",
                nr_vulnerabilities="2",
                file_name=self.file_name,
                file_path=self.file_path,
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_low_warnings(self):
        """Test that the number of warnings is returned."""
        xml = f"""<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <dependency isVirtual="false">
                <sha1>12345</sha1>
                <fileName>{self.file_name}</fileName>
                <filePath>{self.file_path}</filePath>
                <vulnerabilities>
                    <vulnerability source="NVD">
                        <cvssV2>
                            <severity>LOW</severity>
                        </cvssV2>
                    </vulnerability>
                </vulnerabilities>
            </dependency>
        </analysis>"""
        response = await self.collect(self.metric, get_request_text=xml)
        expected_entities = [
            dict(
                key="12345",
                url="https://owasp_dependency_check#l1_12345",
                highest_severity="Low",
                nr_vulnerabilities="1",
                file_name=self.file_name,
                file_path=self.file_path,
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_multiple_warnings_with_same_filepath(self):
        """Test that the hashes are based on both the file path and the file name."""
        xml = """<?xml version="1.0"?>
            <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.5.xsd">
                <dependency>
                    <fileName>CuttingEdge.Conditions:1.2.0.0</fileName>
                    <filePath>packages.config</filePath>
                    <vulnerabilities>
                        <vulnerability source="NVD">
                            <cvssV2>
                                <severity>LOW</severity>
                            </cvssV2>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
                <dependency>
                    <fileName>IdentityModel:1.13.1</fileName>
                    <filePath>packages.config</filePath>
                    <vulnerabilities>
                        <vulnerability source="NVD">
                            <cvssV2>
                                <severity>LOW</severity>
                            </cvssV2>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
            </analysis>"""
        response = await self.collect(self.metric, get_request_text=xml)
        expected_entities = [
            dict(
                key="498ac4bf0c766490ad58cd04a71e07a439b97fc8",
                url="",
                file_name="CuttingEdge.Conditions:1.2.0.0",
                highest_severity="Low",
                nr_vulnerabilities="1",
                file_path="packages.config",
            ),
            dict(
                key="7f5f471406d316dfeb580de2738db563f3c7ac97",
                url="",
                file_name="IdentityModel:1.13.1",
                highest_severity="Low",
                nr_vulnerabilities="1",
                file_path="packages.config",
            ),
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_invalid_xml(self):
        """Test that the number of warnings is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd">
        </analysis>"""
        response = await self.collect(self.metric, get_request_text=xml)
        self.assert_measurement(
            response,
            value=None,
            entities=[],
            parse_error=f"""
AssertionError: The XML root element should be one of \
"{OWASPDependencyCheckBase.allowed_root_tags}" but is \
"{{https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd}}analysis"
""",
        )
