"""Unit tests for the Wekan metric source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class WekanTest(unittest.TestCase):
    """Unit tests for the Wekan metrics."""

    def setUp(self):
        self.metric = dict(
            type="issues", addition="sum",
            sources=dict(
                source_id=dict(
                    type="wekan",
                    parameters=dict(url="http://wekan", board="board", username="user", password="pass"))))

    def test_issues(self):
        """Test that the number of issues and the individual issues are returned."""
        mock_post_response = Mock()
        mock_post_response.json.return_value = dict(token="token")
        mock_get_response = Mock()
        mock_get_response.json.side_effect = [
            dict(slug="board-slug"), [dict(_id="list1")], [dict(_id="card1", title="Card 1")]] * 2
        with patch("requests.post", return_value=mock_post_response):
            with patch("requests.get", return_value=mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card1", url="http://wekan/b/board/board-slug/card1", title="Card 1")],
            response["sources"][0]["units"])
