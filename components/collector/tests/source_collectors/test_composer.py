"""Unit tests for the Composer source."""

from .source_collector_test_case import SourceCollectorTestCase


class ComposerDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the dependencies metric."""
    def setUp(self):
        super().setUp()
        self.composer_json = dict(
            installed=[
                {"name": "package-1", "version": "2.5.2", "latest": "2.6.1", "latest-status": "semver-safe-update",
                 "homepage": "https://url", "description": "description", "warning": "warning"},
                {"name": "package-2", "version": "2.0.0", "latest": "2.0.0", "latest-status": "up-to-date"}])
        self.expected_entities = [
            dict(
                key="package-1@2.5.2", name="package-1", version="2.5.2", latest="2.6.1", homepage="https://url",
                latest_status="semver-safe-update", description="description", warning="warning"),
            dict(
                key="package-2@2.0.0", name="package-2", version="2.0.0", latest="2.0.0", homepage="",
                latest_status="up-to-date", description="", warning="")]
        self.sources = dict(source_id=dict(type="composer", parameters=dict(url="composer.json")))
        self.metric = dict(type="dependencies", sources=self.sources, addition="sum")

    def test_dependencies(self):
        """Test that the number of dependencies is returned."""
        response = self.collect(self.metric, get_request_json_return_value=self.composer_json)
        self.assert_measurement(response, value="2", total="2", entities=self.expected_entities)

    def test_dependencies_by_status(self):
        """Test that the number of dependencies can be filtered by status."""
        self.sources["source_id"]["parameters"]["latest_version_status"] = ["safe update possible"]
        response = self.collect(self.metric, get_request_json_return_value=self.composer_json)
        self.assert_measurement(response, value="1", total="2", entities=self.expected_entities[:1])
