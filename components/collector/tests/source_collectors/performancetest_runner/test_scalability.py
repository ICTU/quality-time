"""Unit tests for the Performancetest-runner source."""

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerScalabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner performance test scalability collector."""

    METRIC_TYPE = "scalability"
    METRIC_ADDITION = "min"

    async def test_scalability(self):
        """Test that the percentage of the max users at which the ramp-up of throughput breaks is returned."""
        html = """<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">74</td></tr>
            </table></html>"""
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="74")

    async def test_scalability_without_breaking_point(self):
        """Test the scalability without breaking point.

        Test that if the percentage of the max users at which the ramp-up of throughput breaks is 100%, the metric
        reports an error (since there is no breaking point).
        """
        html = """<html><table class="config">
            <tr><td class="name">Trendbreak 'scalability' (%)</td><td id="trendbreak_scalability">100</td></tr>
            </table></html>"""
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value=None, parse_error="Traceback")
