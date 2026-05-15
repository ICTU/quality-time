"""Unit tests for the npm dependencies collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class NpmDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the npm dependencies collector."""

    SOURCE_TYPE = "npm"
    METRIC_TYPE = "dependencies"

    def create_npm_json(self, *names: str) -> dict[str, dict[str, str] | list[dict[str, str]]]:
        """Create a npm JSON fixture."""
        all_dependencies: dict[str, dict[str, str] | list[dict[str, str]]] = {
            "@testing-library/jest-dom": [
                {"current": "6.4.6", "wanted": "6.5.0", "latest": "6.5.0", "dependent": "foo", "location": ""},
                {"current": "6.4.6", "wanted": "6.5.0", "latest": "6.5.0", "dependent": "bar", "location": ""},
            ],
            "lodash": {"current": "4.17.20", "wanted": "4.17.21", "latest": "4.17.21", "location": ""},
            "react": {"wanted": "16.13.1", "latest": "16.13.1", "location": ""},
            "react-dom": {"current": "16.12.0", "wanted": "16.13.1", "latest": "16.13.1", "location": ""},
            "weird-pkg": {"current": "not-a-version", "wanted": "not-a-version", "latest": "latest", "location": ""},
            "zod": {"current": "3.25.76", "wanted": "3.25.76", "latest": "4.2.1", "location": ""},
        }
        return {name: dependency for name, dependency in all_dependencies.items() if name in names or not names}

    def expected_entities(self, *names) -> list[dict[str, str]]:
        """Return the expected entities."""
        all_entities = [
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
            {"key": "lodash@4_17_20", "name": "lodash", "current": "4.17.20", "wanted": "4.17.21", "latest": "4.17.21"},
            {"key": "react@?", "name": "react", "current": "unknown", "wanted": "16.13.1", "latest": "16.13.1"},
            {
                "key": "react-dom@16_12_0",
                "name": "react-dom",
                "current": "16.12.0",
                "wanted": "16.13.1",
                "latest": "16.13.1",
            },
            {
                "key": "weird-pkg@not-a-version",
                "name": "weird-pkg",
                "current": "not-a-version",
                "wanted": "not-a-version",
                "latest": "latest",
            },
            {"key": "zod@3_25_76", "name": "zod", "current": "3.25.76", "wanted": "3.25.76", "latest": "4.2.1"},
        ]
        return [entity for entity in all_entities if entity["name"] in names or not names]

    async def test_dependencies(self):
        """Test that the number of dependencies is returned."""
        npm_json = self.create_npm_json()
        expected_entities = self.expected_entities()
        measurement = await self.collect_measurement(get_request_json_return_value=npm_json)
        self.assert_measurement(measurement, value="7", total="7", entities=expected_entities)

    async def test_multiple_dependents_per_dependency(self):
        """Test that the number of dependencies is returned if a dependency has multiple dependents."""
        npm_json = self.create_npm_json("@testing-library/jest-dom")
        expected_entities = self.expected_entities("@testing-library/jest-dom (foo)", "@testing-library/jest-dom (bar)")
        measurement = await self.collect_measurement(get_request_json_return_value=npm_json)
        self.assert_measurement(measurement, value="2", total="2", entities=expected_entities)

    async def test_filter_major_updates_only(self):
        """Test that only major updates are included when the user selects 'major'."""
        self.set_source_parameter("updates_to_include", ["major"])
        npm_json = self.create_npm_json("lodash", "react-dom", "zod")
        expected_entities = self.expected_entities("zod")
        measurement = await self.collect_measurement(get_request_json_return_value=npm_json)
        self.assert_measurement(measurement, value="1", total="3", entities=expected_entities)

    async def test_filter_minor_updates_only(self):
        """Test that only minor updates are included when the user selects 'minor'."""
        self.set_source_parameter("updates_to_include", ["minor"])
        npm_json = self.create_npm_json("lodash", "react-dom", "zod")
        expected_entities = self.expected_entities("react-dom")
        measurement = await self.collect_measurement(get_request_json_return_value=npm_json)
        self.assert_measurement(measurement, value="1", total="3", entities=expected_entities)

    async def test_filter_patch_updates_only(self):
        """Test that only patch updates are included when the user selects 'patch'."""
        self.set_source_parameter("updates_to_include", ["patch"])
        npm_json = self.create_npm_json("lodash", "react-dom", "zod")
        expected_entities = self.expected_entities("lodash")
        measurement = await self.collect_measurement(get_request_json_return_value=npm_json)
        self.assert_measurement(measurement, value="1", total="3", entities=expected_entities)

    async def test_non_semver_version_is_kept(self):
        """Test that dependencies with non-semver versions are not filtered out."""
        self.set_source_parameter("updates_to_include", ["major"])
        npm_json = self.create_npm_json("weird-pkg")
        expected_entities = self.expected_entities("weird-pkg")
        measurement = await self.collect_measurement(get_request_json_return_value=npm_json)
        self.assert_measurement(measurement, value="1", total="1", entities=expected_entities)
