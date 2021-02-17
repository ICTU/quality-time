"""Base classes for unit tests of the Wekan collectors."""

from typing import Dict

from ...source_collector_test_case import SourceCollectorTestCase


class WekanTestCase(SourceCollectorTestCase):
    """Base class for testing Wekan collectors."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to setup the Wekan source and source data."""
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="wekan",
                parameters=dict(
                    url="https://wekan",
                    board="board1",
                    username="user",
                    password="pass",
                    inactive_days="90",
                    lists_to_ignore=[],
                ),
            )
        )
        self.metric = dict(type=self.METRIC_TYPE, addition=self.METRIC_TYPE, sources=self.sources)
        self.json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1", slug="board-slug")],
            [self.list(1), self.list(2), self.list(3, archived=True)],
            [self.card(1), self.card(2)],
            self.full_card(1),
            self.full_card(2),
            [self.card(3)],
            self.full_card(3),
        ]
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
            key=f"card{card_index}",
            url=f"https://wekan/b/board1/board-slug/card{card_index}",
            title=f"Card {card_index}",
            list=f"List {list_index}",
            due_date="",
            date_last_activity="2019-01-01",
        )
