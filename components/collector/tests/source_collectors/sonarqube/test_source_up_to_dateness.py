"""Unit tests for the SonarQube source up-to-dateness collector."""

from datetime import datetime, timedelta, timezone

from collector_utilities.date_time import days_ago

from .base import SonarQubeTestCase


class SonarQubeSourceUpToDatenessTest(SonarQubeTestCase):
    """Unit tests for the SonarQube source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the number of days since the last analysis is returned."""
        json = {"analyses": [{"date": "2019-03-29T14:20:15+0100"}]}
        response = await self.collect(get_request_json_return_value=json)
        timezone_info = timezone(timedelta(hours=1))
        expected_age = days_ago(datetime(2019, 3, 29, 14, 20, 15, tzinfo=timezone_info))
        self.assert_measurement(
            response,
            value=str(expected_age),
            landing_url="https://sonarqube/project/activity?id=id&branch=master",
        )
