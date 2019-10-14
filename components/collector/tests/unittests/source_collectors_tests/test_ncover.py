"""Unit tests for the NCover source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class NCoverTest(SourceCollectorTestCase):
    """Unit tests for the NCover metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="ncover", parameters=dict(url="https://ncover/report.html")))

    def test_uncovered_lines(self):
        """Test that the number of uncovered sequence points is returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
        <script type="text/javascript">
            Other javascript
        </script>
        <script type="text/javascript">
            ncover.execution.stats = {
                "sequencePointCoverage": {
                    "coveragePoints": 17153,
                    "coveredPoints": 14070
                }
            };
        </script>""")
        self.assert_value(f"{17153-14070}", response)
        self.assert_total("17153", response)

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
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
            </script>""")
        self.assert_value(f"{12034-9767}", response)
        self.assert_total("12034", response)

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
         <script type="text/javascript">
            ncover.serverRoot = 'http://127.0.0.1:11235';
            ncover.createDateTime = '1440425155042';
        </script>""")
        report_datetime = datetime.fromtimestamp(1440425155042 / 1000.)
        expected_age = (datetime.now(tz=report_datetime.tzinfo) - report_datetime).days
        self.assert_value(str(expected_age), response)
