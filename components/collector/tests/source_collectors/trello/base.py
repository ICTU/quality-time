"""Unit tests for the Trello metric source."""

from ..source_collector_test_case import SourceCollectorTestCase


class TrelloTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Trello collectors."""

    SOURCE_TYPE = "trello"

    def setUp(self) -> None:
        """Extend to set up the Trello source and source data."""
        super().setUp()
        self.set_source_parameter("board", "board1")
        self.cards = dict(
            id="board1",
            url="https://trello/board1",
            dateLastActivity="2019-02-10",
            cards=[
                dict(
                    id="card1",
                    name="Card 1",
                    idList="list1",
                    due=None,
                    dateLastActivity="2019-03-03",
                    url="https://trello/card1",
                ),
                dict(
                    id="card2",
                    name="Card 2",
                    idList="list2",
                    due="2019-01-01",
                    dateLastActivity="2019-01-01",
                    url="https://trello/card2",
                ),
            ],
            lists=[dict(id="list1", name="List 1"), dict(id="list2", name="List 2")],
        )
        self.json = [[dict(id="board1", name="Board1")], self.cards, self.cards]
        self.entities = [
            dict(
                key="card1",
                url="https://trello/card1",
                title="Card 1",
                list="List 1",
                due_date=None,
                date_last_activity="2019-03-03",
            ),
            dict(
                key="card2",
                url="https://trello/card2",
                title="Card 2",
                list="List 2",
                due_date="2019-01-01",
                date_last_activity="2019-01-01",
            ),
        ]
