"""Base classes for unit tests of the Wekan collectors."""

from ..source_collector_test_case import SourceCollectorTestCase


class WekanTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Wekan collectors."""

    SOURCE_TYPE = "wekan"

    def setUp(self):
        """Extend to setup the Wekan source and source data."""
        super().setUp()
        self.set_source_parameter("board", "board1")
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
    def card(index: int) -> dict:
        """Create a card."""
        return dict(_id=f"card{index}", title=f"Card {index}")

    @classmethod
    def full_card(cls, index: int) -> dict:
        """Create a full card."""
        return dict(archived=False, boardId="board1", dateLastActivity="2019-01-01", **cls.card(index))

    @staticmethod
    def list(index: int, archived: bool = False) -> dict:
        """Create a list."""
        return dict(_id=f"list{index}", title=f"List {index}", archived=archived)

    @staticmethod
    def entity(card_index: int, list_index: int) -> dict:
        """Return an entity."""
        return dict(
            key=f"card{card_index}",
            url=f"https://wekan/b/board1/board-slug/card{card_index}",
            title=f"Card {card_index}",
            list=f"List {list_index}",
            due_date="",
            date_last_activity="2019-01-01",
        )

    async def get_wekan_response(self):
        """Pass the Wekan JSON and a token."""
        return await self.collect(
            get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token")
        )
