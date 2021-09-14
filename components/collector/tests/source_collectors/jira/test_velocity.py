"""Unit tests for the Jira velocity collector."""

from .base import JiraTestCase


class JiraVelocityTest(JiraTestCase):
    """Unit tests for the Jira velocity collector."""

    METRIC_TYPE = "velocity"

    def setUp(self):
        """Extend to prepare fake Jira data."""
        super().setUp()
        base_url = f"{self.url}/secure/RapidBoard.jspa?rapidView=2&view=reporting&chart="
        self.sprint_url = f"{base_url}sprintRetrospective&sprint="
        self.landing_url = f"{base_url}velocityChart"
        self.boards_json1 = dict(
            maxResults=2, startAt=0, isLast=False, values=[dict(id=0, name="Board 0"), dict(id=1, name="Board 1")]
        )
        self.boards_json2 = dict(
            maxResults=2, startAt=2, isLast=True, values=[dict(id=2, name="Board 2"), dict(id=3, name="Board 3")]
        )
        self.velocity_json = dict(
            sprints=[
                dict(id=4, name="Sprint 4", goal="Goal 4"),
                dict(id=3, name="Sprint 3", goal="Goal 3"),
                dict(id=2, name="Sprint 2", goal=""),
            ],
            velocityStatEntries={
                "2": dict(estimated=dict(value=65, text="65.0"), completed=dict(value=30, text="30.0")),
                "3": dict(estimated=dict(value=62, text="62.0"), completed=dict(value=48, text="48.0")),
                "4": dict(estimated=dict(value=40, text="40.0"), completed=dict(value=42, text="42.0")),
            },
        )

    def sprint_entity(self, key: str, points_completed: float, points_committed: float, goal: bool = True):
        """Create an entity."""
        velocity_type = self.sources["source_id"]["parameters"].get("velocity_type", "completed points")
        points_difference = str(points_completed - points_committed)
        points_measured = {
            "completed points": points_completed,
            "committed points": points_committed,
            "completed points minus committed points": points_difference,
        }[velocity_type]
        return dict(
            key=key,
            name=f"Sprint {key}",
            goal=f"Goal {key}" if goal else "",
            points_completed=str(points_completed),
            points_committed=str(points_committed),
            points_difference=str(points_difference),
            points_measured=str(points_measured),
            url=self.sprint_url + key,
        )

    async def test_completed_velocity(self):
        """Test that the completed velocity is returned."""
        response = await self.collect(
            get_request_json_side_effect=[self.boards_json1, self.boards_json2, self.velocity_json]
        )
        self.assert_measurement(
            response,
            value="40",
            landing_url=self.landing_url,
            entities=[
                self.sprint_entity(key="4", points_completed=42.0, points_committed=40.0),
                self.sprint_entity(key="3", points_completed=48.0, points_committed=62.0),
                self.sprint_entity(key="2", points_completed=30.0, points_committed=65.0, goal=False),
            ],
        )

    async def test_committed_velocity(self):
        """Test that the committed velocity is returned."""
        self.set_source_parameter("velocity_type", "committed points")
        response = await self.collect(
            get_request_json_side_effect=[self.boards_json1, self.boards_json2, self.velocity_json]
        )
        self.assert_measurement(
            response,
            value="56",
            landing_url=self.landing_url,
            entities=[
                self.sprint_entity(key="4", points_completed=42.0, points_committed=40.0),
                self.sprint_entity(key="3", points_completed=48.0, points_committed=62.0),
                self.sprint_entity(key="2", points_completed=30.0, points_committed=65.0, goal=False),
            ],
        )

    async def test_velocity_difference(self):
        """Test that the difference between completed and committed velocity is returned."""
        self.set_source_parameter("velocity_type", "completed points minus committed points")
        response = await self.collect(
            get_request_json_side_effect=[self.boards_json1, self.boards_json2, self.velocity_json]
        )
        self.assert_measurement(
            response,
            value="-16",
            landing_url=self.landing_url,
            entities=[
                self.sprint_entity(key="4", points_completed=42.0, points_committed=40.0),
                self.sprint_entity(key="3", points_completed=48.0, points_committed=62.0),
                self.sprint_entity(key="2", points_completed=30.0, points_committed=65.0, goal=False),
            ],
        )

    async def test_velocity_missing_board(self):
        """Test that no velocity is returned if the board name or id is invalid."""
        boards_json = dict(startAt=0, maxResults=50, isLast=True, values=[dict(id=1, name="Board 1")])
        response = await self.collect(get_request_json_side_effect=[boards_json])
        self.assert_measurement(
            response, connection_error="Could not find a Jira board with id or name", landing_url=self.url
        )
