"""Unit tests for the OJAudit source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector


class OJAuditTest(unittest.TestCase):
    """Unit tests for the OJAudit metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.text = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <construct>
    <name>a</name>
    <children>
      <construct>
        <name>b</name>
        <children>
          <violation>
            <message>b</message>
            <location>
              <line-number>20</line-number>
            </location>
          </violation>
        </children>
      </construct>
      <violation>
        <message>a</message>
        <location>
          <line-number>10</line-number>
        </location>
      </violation>
    </children>
  </construct>
</audit>"""
        sources = dict(
            a=dict(type="ojaudit", parameters=dict(url="http://ojaudit.xml")))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("violations", sources)
        self.assertEqual([dict(component="a:10", key="a:a:10", message="a", url="http://ojaudit.html"),
                          dict(component="b:20", key="b:b:20", message="b", url="http://ojaudit.html")],
                         response["sources"][0]["units"])
        self.assertEqual("2", response["sources"][0]["value"])
