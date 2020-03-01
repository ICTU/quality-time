"""Unit tests for the Trello metric source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class TrelloTestCase(SourceCollectorTestCase):
    """Base class for testing Trello collectors."""

    def setUp(self) -> None:
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="trello",
                parameters=dict(
                    url="https://trello",
                    board="board1",
                    api_key="abcdef123",
                    token="4533dea",
                    inactive_days="30",
                    lists_to_ignore=[])))
        self.cards = dict(
            id="board1", url="https://trello/board1", dateLastActivity="2019-02-10",
            cards=[
                dict(
                    id="card1", name="Card 1", idList="list1", due=None, dateLastActivity="2019-03-03",
                    url="https://trello/card1"),
                dict(
                    id="card2", name="Card 2", idList="list2", due="2019-01-01", dateLastActivity="2019-01-01",
                    url="https://trello/card2")],
            lists=[dict(id="list1", name="List 1"), dict(id="list2", name="List 2")])
        self.entities = [
            dict(key="card1", url="https://trello/card1", title="Card 1", list="List 1", due_date=None,
                 date_last_activity="2019-03-03"),
            dict(key="card2", url="https://trello/card2", title="Card 2", list="List 2",
                 due_date="2019-01-01", date_last_activity="2019-01-01")]


class TrelloIssuesTest(TrelloTestCase):
    """Unit tests for the Trello issue metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", addition="sum", sources=self.sources)
        self.json = [[dict(id="board1", name="Board1")], self.cards, self.cards]

    async def test_issues(self):
        """Test that the number of issues and the individual issues are returned."""
        response = await self.collect(self.metric, get_request_json_side_effect=self.json)
        self.assert_measurement(response, value="2", entities=self.entities)

    async def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        response = await self.collect(self.metric, get_request_json_side_effect=self.json)
        self.assert_measurement(response, value="1", entities=[self.entities[1]])

    async def test_overdue_issues(self):
        """Test overdue issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        response = await self.collect(self.metric, get_request_json_side_effect=self.json)
        self.assert_measurement(response, value="1", entities=[self.entities[1]])

    async def test_inactive_issues(self):
        """Test inactive issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        self.cards["cards"][0]["dateLastActivity"] = datetime.now().isoformat()
        response = await self.collect(self.metric, get_request_json_side_effect=self.json)
        self.assert_measurement(response, value="1", entities=[self.entities[1]])


class TrelloSourceUpToDatenessTest(TrelloTestCase):
    """Unit tests for the Trello source up-to-dateness metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        self.side_effect = [[dict(id="board1", name="Board1")], self.cards, self.cards]

    async def test_age(self):
        """Test that the source up to dateness is the number of days since the most recent change."""
        response = await self.collect(self.metric, get_request_json_side_effect=self.side_effect)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 3, 3)).days))

    async def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the source up to dateness."""
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        response = await self.collect(self.metric, get_request_json_side_effect=self.side_effect)
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 2, 10)).days))
