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
                    url="http://wekan", board="board1", username="user", password="pass",
                    inactive_days="90", lists_to_ignore=[])))


class WekanIssuesTest(WekanTestCase):
    """Unit tests for the Wekan issues collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", addition="sum", sources=self.sources)

    def test_issues(self):
        """Test that the number of issues and the individual issues are returned and that archived cards are ignored."""
        json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=True, boardId="board1", dateLastActivity="2019-01-01")]
        response = self.collect(
            self.metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_value("1", response)
        self.assert_entities(
            [dict(key="card1", url="http://wekan/b/board1/board-slug/card1", title="Card 1", list="List 1",
                  due_date="", date_last_activity="2019-01-01")],
            response)

    def test_issues_with_ignored_list(self):
        """Test that lists can be ignored when counting issues."""
        json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False), dict(_id="list2", title="List 2", archived=False),
             dict(_id="list3", archived=True)],
            [dict(_id="card1", title="Card 1")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01")]
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
        response = self.collect(
            self.metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_value("1", response)
        self.assert_entities(
            [dict(key="card1", url="http://wekan/b/board1/board-slug/card1", title="Card 1", list="List 2",
                  due_date="", date_last_activity="2019-01-01")],
            response)

    def test_overdue_issues(self):
        """Test overdue issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["overdue"]
        json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2019-01-01",
                 dueAt="2019-01-01")]
        response = self.collect(
            self.metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_value("1", response)
        self.assert_entities(
            [dict(key="card2", url="http://wekan/b/board1/board-slug/card2", title="Card 2", list="List 1",
                  due_date="2019-01-01", date_last_activity="2019-01-01")],
            response)

    def test_inactive_issues(self):
        """Test inactive issues."""
        self.metric["sources"]["source_id"]["parameters"]["cards_to_count"] = ["inactive"]
        json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(slug="board-slug"),
            [dict(_id="list1", title="List 1", archived=False)],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1",
                 dateLastActivity=datetime.now().isoformat()),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2000-01-01")]
        response = self.collect(
            self.metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_value("1", response)
        self.assert_entities(
            [dict(key="card2", url="http://wekan/b/board1/board-slug/card2", title="Card 2", list="List 1", due_date="",
                  date_last_activity="2000-01-01")],
            response)


class WekanSourceUpToDatenessTest(WekanTestCase):
    """Unit tests for the Wekan source up-to-dateness collector."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)

    def test_age(self):
        """Test that the number of days since the last activity is returned."""
        json = [
            dict(_id="user_id"),
            [dict(_id="board1", title="Board 1")],
            dict(_id="board1", createdAt="2019-01-01"),
            [dict(_id="list1", title="List 1", archived=False, createdAt="2019-01-01")],
            [dict(_id="card1", title="Card 1"), dict(_id="card2", title="Card 2")],
            dict(_id="card1", title="Card 1", archived=False, boardId="board1", dateLastActivity="2019-01-01"),
            dict(_id="card2", title="Card 2", archived=False, boardId="board1", dateLastActivity="2019-01-01")]
        response = self.collect(
            self.metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_value(str((datetime.now() - datetime(2019, 1, 1)).days), response)

    def test_age_with_ignored_lists(self):
        """Test that lists can be ignored when measuring the number of days since the last activity."""
        self.metric["sources"]["source_id"]["parameters"]["lists_to_ignore"] = ["list1"]
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
            self.metric, get_request_json_side_effect=json, post_request_json_return_value=dict(token="token"))
        self.assert_value(str((datetime.now() - datetime(2019, 1, 1)).days), response)
