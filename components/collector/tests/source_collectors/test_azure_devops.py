"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago
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
        self.assert_measurement(response, value="2")

    def test_no_issues(self):
        """Test zero issues."""
        response = self.collect(self.metric, post_request_json_return_value=dict(workItems=[]))
        self.assert_measurement(response, value="0", entities=[])

    def test_issues(self):
        """Test that the issues are returned."""
        response = self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[dict(id="id")]),
            get_request_json_return_value=dict(value=[self.work_item]))
        self.assert_measurement(
            response,
            entities=[dict(
                key="id", project="Project", title="Title", work_item_type="Task", state="New", url="https://url")])


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
        self.assert_measurement(response, value="4")

    def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[]),
            get_request_json_return_value=dict(value=[]))
        self.assert_measurement(response, value="0", entities=[])


class AzureDevopsUnmergedBranchesTest(SourceCollectorTestCase):
    """Unit tests for the Azure DevOps Server unmerged branches."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="azure_devops", parameters=dict(
                    url="https://azure_devops/org/project", private_token="xxx", branches_to_ignore=["ignored_.*"])))
        self.metric = dict(type="unmerged_branches", sources=self.sources, addition="sum")
        self.repositories = dict(value=[dict(id="id", name="project")])

    def test_no_branches_except_master(self):
        """Test that the number of unmerged branches is returned."""
        branches = dict(value=[dict(name="master", isBaseVersion=True)])
        response = self.collect(self.metric, get_request_json_side_effect=[self.repositories, branches])
        self.assert_measurement(
            response, value="0", entities=[], landing_url="https://azure_devops/org/project/_git/project/branches")

    def test_unmerged_branches(self):
        """Test that the number of unmerged branches is returned."""
        branches = dict(
            value=[
                dict(name="master", isBaseVersion=True),
                dict(name="branch", isBaseVersion=False, aheadCount=1,
                     commit=dict(committer=dict(date="2019-09-03T20:43:00Z"))),
                dict(name="ignored_branch", isBaseVersion=False, aheadCount=1,
                     commit=dict(committer=dict(date="2019-09-03T20:43:00Z")))])
        response = self.collect(self.metric, get_request_json_side_effect=[self.repositories, branches])
        expected_age = str(days_ago(parse("2019-09-03T20:43:00Z")))
        self.assert_measurement(
            response,
            value="1",
            entities=[dict(name="branch", key="branch", commit_age=expected_age, commit_date="2019-09-03")],
            landing_url="https://azure_devops/org/project/_git/project/branches")


class AzureDevopsSourceUpToDatenessTest(SourceCollectorTestCase):
    """Unit tests for the Azure DevOps Server source up-to-dateness collector."""

    def test_age(self):
        """Test that the age of the file is returned."""
        sources = dict(
            source_id=dict(
                type="azure_devops",
                parameters=dict(
                    url="https://azure_devops/org/project", repository="repo", private_token="xxx",
                    file_path="README.md")))
        metric = dict(type="source_up_to_dateness", sources=sources, addition="max")
        repositories = dict(value=[dict(id="id", name="repo")])
        commits = dict(value=[dict(committer=dict(date="2019-09-03T20:43:00Z"))])
        response = self.collect(
            metric, get_request_json_side_effect=[repositories, commits])
        expected_age = str(days_ago(parse("2019-09-03T20:43:00Z")))
        self.assert_measurement(
            response,
            value=expected_age,
            landing_url="https://azure_devops/org/project/_git/repo?path=README.md&version=GBmaster")


class AzureDevopsTestsTest(SourceCollectorTestCase):
    """Unit tests for the Azure DevOps Server tests collector."""

    def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        sources = dict(
            source_id=dict(
                type="azure_devops", parameters=dict(url="https://azure_devops", private_token="xxx", test_result=[])))
        metric = dict(type="tests", sources=sources, addition="sum")
        response = self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(build=dict(id="1"), passedTests=2),
                    dict(build=dict(id="2"), passedTests=2, notApplicableTests=1),
                    dict(build=dict(id="1"), passedTests=4),
                    dict(build=dict(id="2"), passedTests=1)]))
        self.assert_measurement(response, value="4")

    def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        sources = dict(
            source_id=dict(
                type="azure_devops",
                parameters=dict(url="https://azure_devops", private_token="xxx", test_result=["failed"])))
        metric = dict(type="tests", sources=sources, addition="sum")
        response = self.collect(
            metric, get_request_json_return_value=dict(value=[dict(build=dict(id="1"), unanalyzedTests=4)]))
        self.assert_measurement(response, value="4")


class AzureDevopsFailedJobsTest(SourceCollectorTestCase):
    """Unit tests for the Azure Devops Server failed jobs collector."""

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned, that pipelines can be ignored by status, by name, and by
        regular expression."""
        sources = dict(
            source_id=dict(
                type="azure_devops",
                parameters=dict(
                    url="https://azure_devops", private_token="xxx", failure_type=["failed"],
                    jobs_to_ignore=["ignore_by_name", "folder/ignore.*"])))
        metric = dict(type="failed_jobs", sources=sources, addition="sum")
        response = self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(path=r"\\folder", name="pipeline", _links=dict(web=dict(href="https://azure_devops/build")),
                         latestCompletedBuild=dict(result="failed", finishTime="2019-11-15T12:24:10.1905868Z")),
                    dict(path=r"\\folder\\subfolder", name="pipeline", latestCompletedBuild=dict(result="canceled")),
                    dict(path=r"\\folder", name="ignore_by_re", latestCompletedBuild=dict(result="failed")),
                    dict(path=r"\\", name="ignore_by_name", latestCompletedBuild=dict(result="failed")),
                    dict(path=r"\\", name="no_builds")
                ]))
        expected_age = days_ago(parse("2019-11-15T12:24:10.1905868Z"))
        self.assert_measurement(
            response, value="1",
            api_url="https://azure_devops/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1",
            landing_url="https://azure_devops/_build",
            entities=[
                dict(name=r"folder/pipeline", key=r"folder/pipeline", url="https://azure_devops/build",
                     build_date="2019-11-15", build_age=str(expected_age), build_status="failed")])

    def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned, that pipelines can be ignored by name and by
        regular expression."""
        sources = dict(
            source_id=dict(
                type="azure_devops",
                parameters=dict(
                    url="https://azure_devops", private_token="xxx",
                    jobs_to_ignore=["ignore_by_name", "folder/ignore.*"])))
        metric = dict(type="unused_jobs", sources=sources, addition="sum")
        response = self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(path=r"\\folder", name="pipeline", _links=dict(web=dict(href="https://azure_devops/build")),
                         latestCompletedBuild=dict(result="failed", finishTime="2019-10-15T12:24:10.1905868Z")),
                    dict(path=r"\\folder", name="ignore_by_re", latestCompletedBuild=dict(result="failed")),
                    dict(path=r"\\", name="ignore_by_name", latestCompletedBuild=dict(result="failed"))
                ]))
        expected_age = days_ago(parse("2019-10-15T12:24:10.1905868Z"))
        self.assert_measurement(
            response, value="1",
            api_url="https://azure_devops/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1",
            landing_url="https://azure_devops/_build",
            entities=[
                dict(name=r"folder/pipeline", key=r"folder/pipeline", url="https://azure_devops/build",
                     build_date="2019-10-15", build_age=str(expected_age), build_status="failed")])
