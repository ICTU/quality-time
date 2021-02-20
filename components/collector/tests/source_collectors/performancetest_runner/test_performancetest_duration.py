"""Unit tests for the Performancetest-runner performancetest duration source."""

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerDurationTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner duration collector."""

    METRIC_TYPE = "performancetest_duration"
    METRIC_ADDITION = "min"

    async def test_duration(self):
        """Test that the test duration is returned."""
        html = (
            '<html><table class="config"><tr><td class="name">Duration</td>'
            '<td id="duration">00:35:00</td></tr></table></html>'
        )
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="35")
