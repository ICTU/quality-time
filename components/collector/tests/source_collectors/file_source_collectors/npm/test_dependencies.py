"""Unit tests for the npm dependencies collector."""

from ...source_collector_test_case import SourceCollectorTestCase


class NpmDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the npm dependencies collector."""

    SOURCE_TYPE = "npm"
    METRIC_TYPE = "dependencies"

    async def test_dependencies(self):
        """Test that the number of dependencies is returned."""
        npm_json = {
            "react": {"wanted": "16.13.1", "latest": "16.13.1", "location": ""},
            "react-dom": {"current": "16.12.0", "wanted": "16.13.1", "latest": "16.13.1", "location": ""},
        }
        expected_entities = [
            dict(key="react@?", name="react", current="unknown", wanted="16.13.1", latest="16.13.1"),
            dict(key="react-dom@16_12_0", name="react-dom", current="16.12.0", wanted="16.13.1", latest="16.13.1"),
        ]
        response = await self.collect(self.metric, get_request_json_return_value=npm_json)
        self.assert_measurement(response, value="2", total="100", entities=expected_entities)
