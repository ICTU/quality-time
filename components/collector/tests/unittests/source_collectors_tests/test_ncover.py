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
        <div id="execution_summary">
            <div class="label">Sequence Points:</div>
            <div class="value">
                <div class="partial larger">82.0%</div>
                <div class="partial smaller">(14068 of 17151)</div>
            <div>
        </div>
        """)
        self.assert_value(f"{17151-14068}", response)
        self.assert_total("17151", response)

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
        <div id="execution_summary">
            <div class="label">Branches:</div>
            <div class="value">
                <div class="partial larger">81.2%</div>
                <div class="partial smaller">(9769 of 12034)</div>
            </div>
        </div>
        """)
        self.assert_value(f"{12034-9769}", response)
        self.assert_total("12034", response)

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
        <div id="execution_summary">
            <div class="label">Collection Date:</div>
            <div class="value">Tue Oct 01 2019 03:04:10</div>
        </div>""")
        expected_age = (datetime.utcnow() - datetime(2019, 10, 1, 3, 4, 10)).days
        self.assert_value(str(expected_age), response)
