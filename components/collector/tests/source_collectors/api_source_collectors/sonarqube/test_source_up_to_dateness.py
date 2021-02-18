"""Unit tests for the SonarQube source up-to-dateness collector."""

from datetime import datetime, timedelta, timezone

from .base import SonarQubeTestCase


class SonarQubeSourceUpToDatenessTest(SonarQubeTestCase):
    """Unit tests for the SonarQube source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the number of days since the last analysis is returned."""
        json = dict(analyses=[dict(date="2019-03-29T14:20:15+0100")])
        response = await self.collect(self.metric, get_request_json_return_value=json)
        timezone_info = timezone(timedelta(hours=1))
        expected_age = (datetime.now(timezone_info) - datetime(2019, 3, 29, 14, 20, 15, tzinfo=timezone_info)).days
        self.assert_measurement(
            response, value=str(expected_age), landing_url="https://sonar/project/activity?id=id&branch=master"
        )
