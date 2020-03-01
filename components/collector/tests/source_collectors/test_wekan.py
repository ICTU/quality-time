"""Unit tests for the Wekan metric source."""

from datetime import datetime
from typing import Dict

from .source_collector_test_case import SourceCollectorTestCase


class WekanTestCase(SourceCollectorTestCase):
    """Base class for testing Wekan collectors."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="wekan",
                parameters=dict(
                    url="https://wekan", board="board1", username="user", password="pass",
                    inactive_days="90", lists_to_ignore=[])))
        self.json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [self.list(1), self.list(2), self.list(3, archived=True)],
            [self.card(1), self.card(2)],
            self.full_card(1),
            self.full_card(2),
            [self.card(3)],
            self.full_card(3)]
        self.entities = [self.entity(1, 1), self.entity(3, 2)]

    @staticmethod
    def card(index: int) -> Dict:
        """Create a card."""
        return dict(_id=f"card{index}", title=f"Card {index}")

    @classmethod
    def full_card(cls, index: int) -> Dict:
        """Create a full card."""
        return dict(archived=False, boardId="board1", dateLastActivity="2019-01-01", **cls.card(index))

    @staticmethod
    def list(index: int, archived: bool = False) -> Dict:
        """Create a list."""
        return dict(_id=f"list{index}", title=f"List {index}", archived=archived)

    @staticmethod
    def entity(card_index: int, list_index: int) -> Dict:
        """Return an entity"""
        return dict(
            key=f"card{card_index}", url=f"https://wekan/b/board1/board-slug/card{card_index}",
            title=f"Card {card_index}", list=f"List {list_index}", due_date="", date_last_activity="2019-01-01")


class WekanIssuesTest(WekanTestCase):
    """Unit tests for the Wekan issues collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", addition="sum", sources=self.sources)

    async def test_issues(self):
        """Test that the number of issues and the individual issues are returned and that archived cards are ignored."""
        self.json[6]["archived"] = True
        response = await self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="2", entities=self.entities)

    async def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.sources["source_id"]["parameters"]["lists_to_ignore"] = ["list2"]
        self.json[6]["archived"] = True
        del self.entities[1]
        response = await self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="1", entities=self.entities)

    async def test_overdue_issues(self):
        """Test overdue issues."""
        self.sources["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        self.entities[0]["due_date"] = self.json[5]["dueAt"] = "2019-01-01"
        self.entities[1]["due_date"] = self.json[8]["dueAt"] = "2019-02-02"
        response = await self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="2", entities=self.entities)

    async def test_inactive_issues(self):
        """Test inactive issues."""
        self.sources["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        self.json[6]["dateLastActivity"] = datetime.now().isoformat()
        response = await self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="2", entities=self.entities)


class WekanSourceUpToDatenessTest(WekanTestCase):
    """Unit tests for the Wekan source up-to-dateness collector."""

    async def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the number of days since the last activity."""
        self.sources["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(
            metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 1, 1)).days))
