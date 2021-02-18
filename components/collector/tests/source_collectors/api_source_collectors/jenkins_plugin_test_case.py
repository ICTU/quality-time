"""Generic unit tests for Jenkins plugin sources."""

from datetime import datetime

from ..source_collector_test_case import SourceCollectorTestCase

from collector_utilities.functions import days_ago


class JenkinsPluginTestCase(SourceCollectorTestCase):
    """Test case for Jenkins plugin sources."""

    SOURCE_TYPE = "Subclass responsibility"
    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to set up the sources and metric under test."""
        super().setUp()
        self.sources = dict(source_id=dict(type=self.SOURCE_TYPE, parameters=dict(url="https://jenkins/job")))
        self.metric = dict(type=self.METRIC_TYPE, addition=self.METRIC_ADDITION, sources=self.sources)


class JenkinsPluginSourceUpToDatenessMixin:  # pylint: disable=too-few-public-methods
    """Unit tests for Jenkins plugin source up-to-dateness collectors to be mixed in."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source up to dateness is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=dict(timestamp="1565284457173"))
        expected_age = days_ago(datetime.fromtimestamp(1565284457173 / 1000.0))
        self.assert_measurement(response, value=str(expected_age))
