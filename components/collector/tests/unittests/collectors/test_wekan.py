"""Unit tests for the Wekan metric source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class WekanTest(unittest.TestCase):
    """Unit tests for the Wekan metrics."""

    def setUp(self):
        self.metric = dict(
            type="issues", addition="sum",
            sources=dict(a=dict(type="wekan", parameters=dict(url="http://wekan", username="user", password="pass"))))

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        mock_post_response = Mock()
        mock_post_response.json.return_value = dict(token="token")
        mock_get_response = Mock()
        mock_get_response.json.side_effect = [[dict(_id="list1")], [dict(_id="card1")]]
        with patch("requests.post", return_value=mock_post_response):
            with patch("requests.get", return_value=mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
