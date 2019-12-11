"""Unit tests for the Wekan metric source."""

from datetime import datetime

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


class WekanIssuesTest(WekanTestCase):
    """Unit tests for the Wekan issues collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", addition="sum", sources=self.sources)
        self.json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False), dict(_id="list2", title="List 2", archived=False),
             dict(_id="list3", archived=True)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            [dict(_id="card3", title="Card 3")],
            dict(_id="card3", title="Card 3", archived=False, boardId="board1", dateLastActivity="2019-01-01")]
        self.entities = [
            dict(key="card1", url="https://wekan/b/board1/board-slug/card1", title="Card 1", list="List 1",
                 due_date="", date_last_activity="2019-01-01"),
            dict(key="card3", url="https://wekan/b/board1/board-slug/card3", title="Card 3", list="List 2",
                 due_date="", date_last_activity="2019-01-01")]

    def test_issues(self):
        """Test that the number of issues and the individual issues are returned and that archived cards are ignored."""
        self.json[6]["archived"] = True
        response = self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="2", entities=self.entities)

    def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        self.sources["source_id"]["parameters"]["lists_to_ignore"] = ["list2"]
        self.json[6]["archived"] = True
        del self.entities[1]
        response = self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="1", entities=self.entities)

    def test_overdue_issues(self):
        """Test overdue issues."""
        self.sources["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        self.entities[0]["due_date"] = self.json[5]["dueAt"] = "2019-01-01"
        self.entities[1]["due_date"] = self.json[8]["dueAt"] = "2019-02-02"
        response = self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="2", entities=self.entities)

    def test_inactive_issues(self):
        """Test inactive issues."""
        self.sources["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        self.json[6]["dateLastActivity"] = datetime.now().isoformat()
        response = self.collect(
            self.metric, get_request_json_side_effect=self.json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value="2", entities=self.entities)


class WekanSourceUpToDatenessTest(WekanTestCase):
    """Unit tests for the Wekan source up-to-dateness collector."""

    def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the number of days since the last activity."""
        self.sources["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(_id="board1", createdAt="2019-01-01"),
            [dict(_id="list1", title="List 1", archived=False, createdAt="2019-01-15"),
             dict(_id="list2", title="List 2", archived=False, createdAt="2019-01-01")],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            []]
        response = self.collect(
            metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_measurement(response, value=str((datetime.now() - datetime(2019, 1, 1)).days))
