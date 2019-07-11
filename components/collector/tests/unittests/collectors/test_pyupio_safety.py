"""Unit tests for the Pyup.io Safety source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import MetricCollector


class PyupioSafetyTest(unittest.TestCase):
    """Unit tests for the security warning metric."""

    def test_warnings(self):
        """Test the number of security warnings."""
        mock_response = Mock()
        mock_response.json = Mock(
            return_value=[["ansible", "<1.9.2", "1.8.5", "Ansible before 1.9.2 does not ...", "25625"]])
        metric = dict(
            type="security_warnings",
            sources=dict(source_id=dict(type="pyupio_safety", parameters=dict(url="safety.json"))),
            addition="sum",
        )
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(package="ansible", key="25625", installed="1.8.5", affected="<1.9.2",
                  vulnerability="Ansible before 1.9.2 does not ...")],
            response["sources"][0]["entities"])
