"""Unit tests for the Performancetest-runner source."""

from .base import PerformanceTestRunnerTestCase

PERFORMANCETEST_RUNNER_HTML = """
<html>
    <table class="config">
        <tr>
            <td class="name">Breaking point stress (#virtual users)</td>
            <td id="trendbreak_scalability_vusers">%s</td>
        </tr>
        <tr>
            <td class="name">Virtual users</td>
            <td id="virtual_users">%s</td>
        </tr>
    </table>
</html>
"""


class PerformanceTestRunnerScalabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner performance test scalability collector."""

    METRIC_TYPE = "scalability"
    METRIC_ADDITION = "min"

    async def test_scalability(self):
        """Test that the number of virtual users at which the ramp-up of throughput breaks is returned."""
        html = PERFORMANCETEST_RUNNER_HTML % (354, 562)
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="354", total="562")

    async def test_scalability_without_breaking_point(self):
        """Test the scalability without breaking point.

        Test that if the number of virtual users at which the ramp-up of throughput breaks is missing, the metric
        does not report an error (despite there being no breaking point).
        """
        html = PERFORMANCETEST_RUNNER_HTML % (0, 0)
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="0", total="0")
