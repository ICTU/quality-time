"""Unit tests for the NCover uncovered branches collector."""

from .base import NCoverTestCase


class NCoverUncoveredBranchesTest(NCoverTestCase):
    """Unit tests for the NCover uncovered branches collector."""

    METRIC_TYPE = "uncovered_branches"
    NCOVER_HTML = """
        <script type="text/javascript">
            Other javascript
        </script>
        <script type="text/javascript">
            ncover.execution.stats = {
                "branchCoverage": {
                    "coveragePoints": 12034,
                    "coveredPoints": 9767
                }
            };
        </script>"""

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        response = await self.collect(get_request_text=self.NCOVER_HTML)
        self.assert_measurement(response, value=f"{12034-9767}", total="12034")

    async def test_zipped_report(self):
        """Test that the coverage can be read from a zip with NCover reports."""
        self.set_source_parameter("url", "https://example.org/report.zip")
        response = await self.collect(get_request_content=self.zipped_report(("ncover.html", self.NCOVER_HTML)))
        self.assert_measurement(response, value=f"{12034-9767}", total="12034")
