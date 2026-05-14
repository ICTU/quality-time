"""Generic unit tests for Jenkins plugin sources."""

from typing import TYPE_CHECKING

from collector_utilities.date_time import datetime_from_timestamp, days_ago

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JenkinsPluginSourceUpToDatenessMixin(SourceCollectorTestCase if TYPE_CHECKING else object):  # type: ignore[misc]
    """Unit tests for Jenkins plugin source up-to-dateness collectors to be mixed in."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness is returned."""
        measurement = await self.collect_measurement(get_request_json_return_value={"timestamp": "1565284457173"})
        expected_age = days_ago(datetime_from_timestamp(1565284457173))
        self.assert_measurement(measurement, value=str(expected_age))
