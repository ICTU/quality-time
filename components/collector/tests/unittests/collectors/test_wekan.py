"""Unit tests for the Wekan metric source."""

from datetime import datetime
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
                        url="http://wekan", board="board1", username="user", password="pass",
                        inactive_days="90", lists_to_ignore=[]))))
        self.mock_post_response = Mock()
        self.mock_post_response.json.return_value = dict(token="token")
        self.mock_get_response = Mock()

    def test_issues(self):
        """Test that the number of issues and the individual issues are returned and that archived cards are ignored."""
        self.mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=True, boardId="board1", dateLastActivity="2019-01-01")]
        with patch("requests.post", return_value=self.mock_post_response):
            with patch("requests.get", return_value=self.mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card1", url="http://wekan/b/board1/board-slug/card1", title="Card 1", list="List 1",
                  due_date="", date_last_activity="2019-01-01")],
            response["sources"][0]["units"])

    def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False), dict(_id="list2", title="List 2", archived=False),
             dict(_id="list3", archived=True)],
            [dict(_id="card1", title="Card 1")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01")]
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        with patch("requests.post", return_value=self.mock_post_response):
            with patch("requests.get", return_value=self.mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card1", url="http://wekan/b/board1/board-slug/card1", title="Card 1", list="List 2",
                  due_date="", date_last_activity="2019-01-01")],
            response["sources"][0]["units"])

    def test_overdue_issues(self):
        """Test overdue issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        self.mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2019-01-01",
                 dueAt="2019-01-01")]
        with patch("requests.post", return_value=self.mock_post_response):
            with patch("requests.get", return_value=self.mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card2", url="http://wekan/b/board1/board-slug/card2", title="Card 2", list="List 1",
                  due_date="2019-01-01", date_last_activity="2019-01-01")],
            response["sources"][0]["units"])

    def test_inactive_issues(self):
        """Test inactive issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        self.mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1",
                 dateLastActivity=datetime.now().isoformat()),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2000-01-01")]
        with patch("requests.post", return_value=self.mock_post_response):
            with patch("requests.get", return_value=self.mock_get_response):
                response = collect_measurement(self.metric)
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card2", url="http://wekan/b/board1/board-slug/card2", title="Card 2", list="List 1", due_date="",
                  date_last_activity="2000-01-01")],
            response["sources"][0]["units"])


class WekanSourceUpToDatenessTest(unittest.TestCase):
    """Unit tests for the Wekan source up-to-dateness collector."""

    def test_age(self):
        """Test that the number of days since the last activity is returned."""
        metric = dict(
            type="source_up_to_dateness", addition="max",
            sources=dict(
                source_id=dict(
                    type="wekan",
                    parameters=dict(
                        url="http://wekan", board="board1", username="user", password="pass"))))
        mock_post_response = Mock()
        mock_post_response.json.return_value = dict(token="token")
        mock_get_response = Mock()
        mock_get_response.json.side_effect = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(_id="board1", createdAt="2019-01-01"),
            [dict(_id="list1", title="List 1", archived=False, createdAt="2019-01-01")],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2019-01-01")]
        with patch("requests.post", return_value=mock_post_response):
            with patch("requests.get", return_value=mock_get_response):
                response = collect_measurement(metric)
        self.assertEqual(str((datetime.now() - datetime(2019, 1, 1)).days), response["sources"][0]["value"])
