"""Unit tests for the npm dependencies collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


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
            {"key": "react@?", "name": "react", "current": "unknown", "wanted": "16.13.1", "latest": "16.13.1"},
            {
                "key": "react-dom@16_12_0",
                "name": "react-dom",
                "current": "16.12.0",
                "wanted": "16.13.1",
                "latest": "16.13.1",
            },
        ]
        response = await self.collect(get_request_json_return_value=npm_json)
        self.assert_measurement(response, value="2", total="100", entities=expected_entities)

    async def test_multiple_dependents_per_dependency(self):
        """Test that the number of dependencies is returned if a dependency has multiple dependents."""
        npm_json = {
            "@testing-library/jest-dom": [
                {"current": "6.4.6", "wanted": "6.5.0", "latest": "6.5.0", "dependent": "foo", "location": ""},
                {"current": "6.4.6", "wanted": "6.5.0", "latest": "6.5.0", "dependent": "bar", "location": ""},
            ]
        }
        expected_entities = [
            {
                "key": "@testing-library-jest-dom@6_4_6@foo",
                "name": "@testing-library/jest-dom (foo)",
                "current": "6.4.6",
                "wanted": "6.5.0",
                "latest": "6.5.0",
            },
            {
                "key": "@testing-library-jest-dom@6_4_6@bar",
                "name": "@testing-library/jest-dom (bar)",
                "current": "6.4.6",
                "wanted": "6.5.0",
                "latest": "6.5.0",
            },
        ]
        response = await self.collect(get_request_json_return_value=npm_json)
        self.assert_measurement(response, value="2", total="100", entities=expected_entities)
