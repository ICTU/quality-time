"""Generic unit tests for Jenkins plugin sources."""

from datetime import datetime

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase

from collector_utilities.functions import days_ago


class JenkinsPluginTestCase(SourceCollectorTestCase):
    """Test case for Jenkins plugin sources."""

    source_type = "subclass responsbility"

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type=self.source_type, parameters=dict(url="https://jenkins/job")))


class JenkinsPluginTestsMixin:  # pylint: disable=too-few-public-methods
    """Generic unit tests for Jenkins plugin sources to be mixed in."""

    async def test_source_up_to_dateness(self):
        """Test that the source up to dateness is returned."""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=dict(timestamp="1565284457173"))
        expected_age = days_ago(datetime.fromtimestamp(1565284457173 / 1000.))
        self.assert_measurement(response, value=str(expected_age))
