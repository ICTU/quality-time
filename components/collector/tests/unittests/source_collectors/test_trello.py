"""Unit tests for the Trello metric source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from metric_collectors import MetricCollector


class TrelloIssuesTest(unittest.TestCase):
    """Unit tests for the Trello issue metric."""

    def setUp(self):
        self.metric = dict(
            type="issues", addition="sum",
            sources=dict(
                source_id=dict(
                    type="trello",
                    parameters=dict(
                        url="http://trello", board="board1", api_key="abcdef123", token="4533dea",
                        inactive_days="30", lists_to_ignore=[]))))
        self.mock_get_response = Mock()

    def test_issues(self):
        """Test that the number of issues and the individual issues are returned."""
        cards = dict(
            id="board1", url="http://trello/board1",
            cards=[
                dict(
                    id="card1", name="Card 1", idList="list1", due=None, dateLastActivity="2019-01-01",
                    url="http://trello/card1")],
            lists=[dict(id="list1", name="List 1")])
        self.mock_get_response.json.side_effect = [[dict(id="board1", name="Board1")], cards, cards, cards]
        with patch("requests.get", return_value=self.mock_get_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(
                key="card1", url="http://trello/card1", title="Card 1", list="List 1", due_date=None,
                date_last_activity="2019-01-01")],
            response["sources"][0]["entities"])

    def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        cards = dict(
            id="board1", url="http://trello/board1",
            cards=[
                dict(
                    id="card1", name="Card 1", idList="list1", due=None, dateLastActivity="2019-01-01",
                    url="http://trello/card1"),
                dict(
                    id="card2", name="Card 2", idList="list2", due=None, dateLastActivity="2019-01-01",
                    url="http://trello/card2")],
            lists=[dict(id="list1", name="List 1"), dict(id="list2", name="List 2")])
        self.mock_get_response.json.side_effect = [[dict(id="board1", name="Board1")], cards, cards, cards]
        with patch("requests.get", return_value=self.mock_get_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card2", url="http://trello/card2", title="Card 2", list="List 2",
                  due_date=None, date_last_activity="2019-01-01")],
            response["sources"][0]["entities"])

    def test_overdue_issues(self):
        """Test overdue issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        cards = dict(
            id="board1", url="http://trello/board1",
            cards=[
                dict(
                    id="card1", name="Card 1", idList="list1", due=None, dateLastActivity="2019-01-01",
                    url="http://trello/card1"),
                dict(
                    id="card2", name="Card 2", idList="list1", due="2019-01-01", dateLastActivity="2019-01-01",
                    url="http://trello/card2")],
            lists=[dict(id="list1", name="List 1")])
        self.mock_get_response.json.side_effect = [[dict(id="board1", name="Board1")], cards, cards, cards]
        with patch("requests.get", return_value=self.mock_get_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card2", url="http://trello/card2", title="Card 2", list="List 1",
                  due_date="2019-01-01", date_last_activity="2019-01-01")],
            response["sources"][0]["entities"])

    def test_inactive_issues(self):
        """Test inactive issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        cards = dict(
            id="board1", url="http://trello/board1",
            cards=[
                dict(
                    id="card1", name="Card 1", idList="list1", due=None,
                    dateLastActivity=datetime.now().isoformat(), url="http://trello/card1"),
                dict(
                    id="card2", name="Card 2", idList="list1", due=None, dateLastActivity="2019-01-01",
                    url="http://trello/card2")],
            lists=[dict(id="list1", name="List 1")])
        self.mock_get_response.json.side_effect = [[dict(id="board1", name="Board1")], cards, cards, cards]
        with patch("requests.get", return_value=self.mock_get_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("1", response["sources"][0]["value"])
        self.assertEqual(
            [dict(key="card2", url="http://trello/card2", title="Card 2", list="List 1", due_date=None,
                  date_last_activity="2019-01-01")],
            response["sources"][0]["entities"])


class TrelloSourceUpToDatenessTest(unittest.TestCase):
    """Unit tests for the Trello source up-to-dateness metric."""

    def test_age(self):
        """Test that the source up to dateness is the number of days since the most recent change."""
        metric = dict(
            type="source_up_to_dateness", addition="max",
            sources=dict(
                source_id=dict(
                    type="trello",
                    parameters=dict(
                        url="http://trello", board="board1", api_key="abcdef123", token="4533dea"))))
        mock_get_response = Mock()
        cards = dict(
            id="board1", url="http://trello/board1",
            dateLastActivity="2019-02-10",
            cards=[
                dict(id="card1", name="Card 1", dateLastActivity="2019-03-03"),
                dict(id="card2", name="Card 2", dateLastActivity="2019-01-01")])
        mock_get_response.json.side_effect = [[dict(id="board1", name="Board1")], cards, cards]
        with patch("requests.get", return_value=mock_get_response):
            response = MetricCollector(metric).get()
        self.assertEqual(str((datetime.now() - datetime(2019, 3, 3)).days), response["sources"][0]["value"])
