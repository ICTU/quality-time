"""Unit tests for the pip source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class PipDependenciesTest(SourceCollectorTestCase):
    """Unit tests for the dependencies metric."""

    async def test_dependencies(self):
        """Test that the number of dependencies is returned."""
        pip_json = [
            {"name": "gitdb2", "version": "2.0.6", "latest_version": "4.0.2", "latest_filetype": "wheel"},
            {"name": "pip", "version": "20.1", "latest_version": "20.1.1", "latest_filetype": "wheel"}]
        expected_entities = [
            dict(key="gitdb2@2_0_6", name="gitdb2", version="2.0.6", latest="4.0.2"),
            dict(key="pip@20_1", name="pip", version="20.1", latest="20.1.1")]
        sources = dict(source_id=dict(type="pip", parameters=dict(url="pip.json")))
        metric = dict(type="dependencies", sources=sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=pip_json)
        self.assert_measurement(response, value="2", total="100", entities=expected_entities)
