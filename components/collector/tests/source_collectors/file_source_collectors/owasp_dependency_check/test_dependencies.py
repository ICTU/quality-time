"""Unit tests for the OWASP Dependency Check dependencies collector."""

from .base import OWASPDependencyCheckTestCase


class OWASPDependencyCheckDependenciesTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    METRIC_TYPE = "dependencies"

    async def test_dependencies(self):
        """Test that the dependencies are returned."""
        xml = f"""<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <dependency isVirtual="false">
                <sha1>9999</sha1>
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
                key="9999",
                url="https://owasp_dependency_check#l1_9999",
                file_name=self.file_name,
                file_path=self.file_path,
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
