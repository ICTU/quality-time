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
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
    <model id="b">
      <file>
        <path>b</path>
      </file>
    </model>
  </models>
  <construct>
    <children>
      <construct>
        <children>
          <violation>
            <message>a</message>
            <location model="a">
              <line-number>20</line-number>
              <column-offset>4</column-offset>
            </location>
            <values>
              <value>medium</value>
            </values>
          </violation>
        </children>
      </construct>
      <violation>
        <message>b</message>
        <location model="b">
          <line-number>10</line-number>
              <column-offset>2</column-offset>
        </location>
        <values>
          <value>high</value>
        </values>
      </violation>
    </children>
  </construct>
</audit>"""
        sources = dict(a=dict(type="ojaudit", parameters=dict(url="http://ojaudit.xml")))
        with patch("requests.get", return_value=mock_response):
            response = Collector().get("violations", sources)
        self.assertEqual(
            [dict(component="a:20:4", key="c448f7237f7527445a340816163b99e3", severity="medium", message="a"),
             dict(component="b:10:2", key="50b0555f38f8474c5d9cbe333680ff83", severity="high", message="b")],
            response["sources"][0]["units"])
        self.assertEqual("2", response["sources"][0]["value"])

    def test_missing_location(self):
        """Test that an exception is raised if the violation location is missing."""
        mock_response = Mock()
        mock_response.text = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
    <model id="b">
      <file>
        <path>b</path>
      </file>
    </model>
  </models>
  <construct>
    <violation>
    <message>a</message>
    <values>
        <value>medium</value>
    </values>
    </violation>
  </construct>
</audit>"""
        sources = dict(a=dict(type="ojaudit", parameters=dict(url="http://ojaudit.xml")))
        with patch("requests.get", return_value=mock_response):
            self.assertTrue(
                "has no location element" in Collector().get("violations", sources)["sources"][0]["parse_error"])
