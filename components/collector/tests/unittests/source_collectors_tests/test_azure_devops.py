"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

from .source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):
    """Base class for testing Azure DevOps collectors."""
    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(type="azure_devops", parameters=dict(url="https://azure_devops", private_token="xxx")))
        self.work_item = dict(
            id="id", url="https://url",
            fields={"System.TeamProject": "Project", "System.Title": "Title", "System.WorkItemType": "Task",
                    "System.State": "New", "Microsoft.VSTS.Scheduling.StoryPoints": 2.0})


class AzureDevopsIssuesTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server issues metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="issues", sources=self.sources, addition="sum")

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[dict(id="id1"), dict(id="id2")]),
            get_request_json_return_value=dict(value=[self.work_item, self.work_item]))
        self.assert_value("2", response)

    def test_no_issues(self):
        """Test zero issues."""
        response = self.collect(self.metric, post_request_json_return_value=dict(workItems=[]))
        self.assert_value("0", response)

    def test_issues(self):
        """Test that the issues are returned."""
        response = self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[dict(id="id")]),
            get_request_json_return_value=dict(value=[self.work_item]))
        self.assert_entities(
            [dict(key="id", project="Project", title="Title", work_item_type="Task", state="New", url="https://url")],
            response)


class AzureDevopsReadyStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server ready story points metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="ready_user_story_points", sources=self.sources, addition="sum")

    def test_story_points(self):
        """Test that the number of story points are returned."""
        response = self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[dict(id="id1"), dict(id="id2")]),
            get_request_json_return_value=dict(value=[self.work_item, self.work_item]))
        self.assert_value("4", response)

    def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[]),
            get_request_json_return_value=dict(value=[]))
        self.assert_value("0", response)
