"""Unit tests for the Performancetest-runner source-up-to-dateness collector."""

from datetime import datetime

from collector_utilities.functions import days_ago

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerSourceUpToDatenessTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the test age is returned."""
        html = (
            '<html><table class="config"><tr><td class="name">Start of the test</td>'
            '<td id="start_of_the_test">2019.06.22.06.23.00</td></tr></table></html>'
        )
        response = await self.collect(self.metric, get_request_text=html)
        expected_age = days_ago(datetime(2019, 6, 22, 6, 23, 0))
        self.assert_measurement(response, value=str(expected_age))
