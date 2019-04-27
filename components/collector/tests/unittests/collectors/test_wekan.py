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
                    parameters=dict(
                        url="http://wekan", board="board1", username="user", password="pass", lists_to_ignore=[]))))
        self.mock_post_response = Mock()
        self.mock_post_response.json.return_value = dict(token="token")
        self.mock_get_response = Mock()

    def test_issues(self):
        """Test that the number of issues and the individual issues are returned."""
        self.mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1")],
            [dict(_id="card1", title="Card 1")],
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1")],
            [dict(_id="card1", title="Card 1")],
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")]]
        with patch("requests.post", return_value=self.mock_post_response):
            with patch("requests.get", return_value=self.mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card1", url="http://wekan/b/board1/board-slug/card1", title="Card 1", list="List 1")],
            response["sources"][0]["units"])

    def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1"), dict(_id="list2", title="List 2")],
            [dict(_id="card1", title="Card 1")],
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1"), dict(_id="list2", title="List 2")],
            [dict(_id="card1", title="Card 1")],
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")]]
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        with patch("requests.post", return_value=self.mock_post_response):
            with patch("requests.get", return_value=self.mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card1", url="http://wekan/b/board1/board-slug/card1", title="Card 1", list="List 2")],
            response["sources"][0]["units"])
