"""Unit tests for the OWASP Dependency Check dependencies collector."""

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
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
