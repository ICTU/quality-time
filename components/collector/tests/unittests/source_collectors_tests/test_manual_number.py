"""Unit tests for the manual number source."""

from .source_collector_test_case import SourceCollectorTestCase


class ManualNumberTest(SourceCollectorTestCase):
    """Unit tests for the manual number metrics."""

    def test_violations(self):
        """Test the number of violations."""
        metric = dict(
            type="violations", addition="sum",
            sources=dict(source_id=dict(type="manual_number", parameters=dict(number="42"))))
        response = self.collect(metric)
        self.assert_value("42", response)
