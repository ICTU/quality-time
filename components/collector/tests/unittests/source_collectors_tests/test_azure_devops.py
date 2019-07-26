"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

from unittest.mock import Mock, patch

from .source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):
    """Base class for testing Azure DevOps collectors."""
    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(type="azure_devops", parameters=dict(url="http://azure_devops", private_token="xxx")))
        self.work_item = dict(
            id="id", url="http://url",
            fields={"System.TeamProject": "Project", "System.Title": "Title", "System.WorkItemType": "Task",
                    "System.State": "New", "Microsoft.VSTS.Scheduling.StoryPoints": 2.0})

    def collect(self, metric, wiql_json=None, work_items_json=None):
        """Collect the metric."""
        wiql_response = Mock()
        wiql_response.json.return_value = wiql_json
        work_items_response = Mock()
        work_items_response.json.return_value = work_items_json
        with patch("requests.post", return_value=wiql_response):
            with patch("requests.get", return_value=work_items_response):
                return super().collect(metric)


class AzureDevopsIssuesTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server issues metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", sources=self.sources, addition="sum")

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = self.collect(
            self.metric, dict(workItems=[dict(id="id1"), dict(id="id2")]), dict(value=[self.work_item, self.work_item]))
        self.assert_value("2", response)

    def test_no_issues(self):
        """Test zero issues."""
        response = self.collect(self.metric, dict(workItems=[]))
        self.assert_value("0", response)

    def test_issues(self):
        """Test that the issues are returned."""
        response = self.collect(self.metric, dict(workItems=[dict(id="id")]), dict(value=[self.work_item]))
        self.assert_entities(
            [dict(key="id", project="Project", title="Title", work_item_type="Task", state="New", url="http://url")],
            response)


class AzureDevopsReadyStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server ready story points metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="ready_user_story_points", sources=self.sources, addition="sum")

    def test_story_points(self):
        """Test that the number of story points are returned."""
        response = self.collect(
            self.metric, dict(workItems=[dict(id="id1"), dict(id="id2")]), dict(value=[self.work_item, self.work_item]))
        self.assert_value("4", response)

    def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = self.collect(self.metric, dict(workItems=[]), dict(value=[]))
        self.assert_value("0", response)
