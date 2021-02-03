"""Unit tests for the Azure Devops Server (formerly Team Foundation Server) source."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago

from ..source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):
    """Base class for testing Azure DevOps collectors."""

    def setUp(self):
        """Extend to add Azure DevOps fixtures."""
        super().setUp()
        self.url = "https://azure_devops/org/project"
        self.work_item_url = "https://work_item"
        self.sources = dict(source_id=dict(type="azure_devops", parameters=dict(url=self.url, private_token="xxx")))
        self.work_item = dict(
            id="id",
            url=self.work_item_url,
            fields={
                "System.TeamProject": "Project",
                "System.Title": "Title",
                "System.WorkItemType": "Task",
                "System.State": "New",
                "Microsoft.VSTS.Scheduling.StoryPoints": 2.0,
            },
        )


class AzureDevopsIssuesTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server issues metric."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="issues", sources=self.sources, addition="sum")

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(
            self.metric,
            post_request_json_return_value=dict(workItems=[dict(id="id1"), dict(id="id2")]),
            get_request_json_return_value=dict(value=[self.work_item, self.work_item]),
        )
        self.assert_measurement(response, value="2")

    async def test_no_issues(self):
        """Test zero issues."""
        response = await self.collect(self.metric, post_request_json_return_value=dict(workItems=[]))
        self.assert_measurement(response, value="0", entities=[])

    async def test_issues(self):
        """Test that the issues are returned."""
        response = await self.collect(
            self.metric,
            post_request_json_return_value=dict(workItems=[dict(id="id")]),
            get_request_json_return_value=dict(value=[self.work_item]),
        )
        self.assert_measurement(
            response,
            entities=[
                dict(
                    key="id",
                    project="Project",
                    title="Title",
                    work_item_type="Task",
                    state="New",
                    url=self.work_item_url,
                )
            ],
        )


class AzureDevopsStoryPointsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server story points metric."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="user_story_points", sources=self.sources, addition="sum")

    async def test_story_points(self):
        """Test that the number of story points are returned."""
        response = await self.collect(
            self.metric,
            post_request_json_return_value=dict(workItems=[dict(id="id1"), dict(id="id2")]),
            get_request_json_return_value=dict(value=[self.work_item, self.work_item]),
        )
        self.assert_measurement(response, value="4")

    async def test_story_points_without_stories(self):
        """Test that the number of story points is zero when there are no work items."""
        response = await self.collect(
            self.metric, post_request_json_return_value=dict(workItems=[]), get_request_json_return_value=dict(value=[])
        )
        self.assert_measurement(response, value="0", entities=[])


class AzureDevopsUnmergedBranchesTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server unmerged branches."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.sources["source_id"]["parameters"]["branches_to_ignore"] = ["ignored_.*"]
        self.metric = dict(type="unmerged_branches", sources=self.sources, addition="sum")
        self.repositories = dict(value=[dict(id="id", name="project")])
        self.landing_url = f"{self.url}/_git/project/branches"

    async def test_no_branches_except_master(self):
        """Test that the number of unmerged branches is returned."""
        branches = dict(value=[dict(name="master", isBaseVersion=True)])
        response = await self.collect(self.metric, get_request_json_side_effect=[self.repositories, branches])
        self.assert_measurement(response, value="0", entities=[], landing_url=self.landing_url)

    async def test_unmerged_branches(self):
        """Test that the number of unmerged branches is returned."""
        timestamp = "2019-09-03T20:43:00Z"
        branches = dict(
            value=[
                dict(name="master", isBaseVersion=True),
                dict(
                    name="branch",
                    isBaseVersion=False,
                    aheadCount=1,
                    commit=dict(committer=dict(date=timestamp), url="https://commit"),
                ),
                dict(
                    name="ignored_branch",
                    isBaseVersion=False,
                    aheadCount=1,
                    commit=dict(committer=dict(date=timestamp)),
                ),
            ]
        )
        response = await self.collect(self.metric, get_request_json_side_effect=[self.repositories, branches])
        self.assert_measurement(
            response,
            value="1",
            landing_url=self.landing_url,
            entities=[dict(name="branch", key="branch", commit_date="2019-09-03", url="https://commit")],
        )


class AzureDevopsSourceUpToDatenessTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server source up-to-dateness collector."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        self.timestamp = "2019-09-03T20:43:00Z"
        self.expected_age = str(days_ago(parse(self.timestamp)))

    async def test_age_of_file(self):
        """Test that the age of the file is returned."""
        self.sources["source_id"]["parameters"]["repository"] = "repo"
        self.sources["source_id"]["parameters"]["file_path"] = "README.md"
        repositories = dict(value=[dict(id="id", name="repo")])
        commits = dict(value=[dict(committer=dict(date=self.timestamp))])
        response = await self.collect(self.metric, get_request_json_side_effect=[repositories, commits])
        self.assert_measurement(
            response, value=self.expected_age, landing_url=f"{self.url}/_git/repo?path=README.md&version=GBmaster"
        )

    async def test_age_of_pipeline(self):
        """Test that the age of the pipeline is returned."""
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["pipeline"]
        response = await self.collect(
            self.metric,
            get_request_json_return_value=dict(
                value=[
                    dict(
                        path=r"\\folder",
                        name="pipeline",
                        _links=dict(web=dict(href=f"{self.url}/build")),
                        latestCompletedBuild=dict(result="failed", finishTime=self.timestamp),
                    )
                ]
            ),
        )
        self.assert_measurement(response, value=self.expected_age, landing_url=f"{self.url}/_build")

    async def test_no_file_path_and_no_pipelines_specified(self):
        """Test that the age of the pipelines is used if no file path and no pipelines are specified."""
        response = await self.collect(
            self.metric,
            get_request_json_return_value=dict(
                value=[
                    dict(
                        path=r"\\folder",
                        name="pipeline",
                        _links=dict(web=dict(href=f"{self.url}/build")),
                        latestCompletedBuild=dict(result="failed", finishTime=self.timestamp),
                    )
                ]
            ),
        )
        self.assert_measurement(response, value=self.expected_age, landing_url=f"{self.url}/_build")


class AzureDevopsTestsTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server tests collector."""

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["passed"]
        self.sources["source_id"]["parameters"]["test_run_names_to_include"] = ["A.*"]
        self.sources["source_id"]["parameters"]["test_run_states_to_include"] = ["completed"]
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(id=1, name="A", build=dict(id="1"), state="Completed", passedTests=2, totalTests=2),
                    dict(
                        id=2,
                        name="A",
                        build=dict(id="2"),
                        state="Completed",
                        startedDate="2020-06-20T14:56:00.58Z",
                        completedDate="2020-06-20T14:56:00.633Z",
                        passedTests=2,
                        notApplicableTests=1,
                        totalTests=3,
                        webAccessUrl="https://azuredevops/project/run",
                    ),
                    dict(id=3, name="A", build=dict(id="1"), state="Completed", passedTests=4, totalTests=4),
                    dict(id=4, name="A", build=dict(id="2"), state="Completed", passedTests=1, totalTests=1),
                    dict(id=5, name="B", build=dict(id="3"), state="Completed", passedTests=5, totalTests=5),
                    dict(id=6, name="A+", build=dict(id="1"), state="Completed", passedTests=6, totalTests=6),
                    dict(id=7, name="A+", build=dict(id="2"), state="InProgress", passedTests=6, totalTests=6),
                ]
            ),
        )
        self.assert_measurement(
            response,
            value="9",
            total="10",
            entities=[
                dict(
                    key="2",
                    name="A",
                    state="Completed",
                    build_id="2",
                    started_date="2020-06-20T14:56:00.58Z",
                    completed_date="2020-06-20T14:56:00.633Z",
                    counted_tests="2",
                    incomplete_tests="0",
                    not_applicable_tests="1",
                    passed_tests="2",
                    unanalyzed_tests="0",
                    total_tests="3",
                    url="https://azuredevops/project/run",
                ),
                dict(
                    key="4",
                    name="A",
                    state="Completed",
                    build_id="2",
                    started_date="",
                    completed_date="",
                    counted_tests="1",
                    incomplete_tests="0",
                    not_applicable_tests="0",
                    passed_tests="1",
                    unanalyzed_tests="0",
                    total_tests="1",
                    url="",
                ),
                dict(
                    key="6",
                    name="A+",
                    state="Completed",
                    build_id="1",
                    started_date="",
                    completed_date="",
                    counted_tests="6",
                    incomplete_tests="0",
                    not_applicable_tests="0",
                    passed_tests="6",
                    unanalyzed_tests="0",
                    total_tests="6",
                    url="",
                ),
            ],
        )

    async def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.sources["source_id"]["test_result"] = ["failed"]
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[dict(id="1", build=dict(id="1"), state="Completed", unanalyzedTests=4)]
            ),
        )
        self.assert_measurement(response, value="4")


class AzureDevopsFailedJobsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server failed jobs collector."""

    def setUp(self):
        """Extend to set up test fixtures."""
        super().setUp()
        self.path = r"\\folder"
        self.pipeline = r"folder/include_pipeline"
        self.api_url = f"{self.url}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1"

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned, that pipelines can be included and ignored by status,
        by name, and by regular expression."""
        self.sources["source_id"]["parameters"]["failure_type"] = ["failed"]
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["include.*"]
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["include_but_ignore_by_name", "folder/.*ignore.*"]
        metric = dict(type="failed_jobs", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(
                        path=self.path,
                        name="include_pipeline",
                        _links=dict(web=dict(href=f"{self.url}/build")),
                        latestCompletedBuild=dict(result="failed", finishTime="2019-11-15T12:24:10.1905868Z"),
                    ),
                    dict(
                        path=fr"{self.path}\\subfolder",
                        name="include_pipeline",
                        latestCompletedBuild=dict(result="canceled"),
                    ),
                    dict(path=self.path, name="include_but_ignore_by_re", latestCompletedBuild=dict(result="failed")),
                    dict(path=r"\\", name="include_but_ignore_by_name", latestCompletedBuild=dict(result="failed")),
                    dict(path=r"\\", name="include_but_no_builds"),
                ]
            ),
        )
        self.assert_measurement(
            response,
            value="1",
            landing_url=f"{self.url}/_build",
            api_url=self.api_url,
            entities=[
                dict(
                    name=self.pipeline,
                    key=self.pipeline.replace("/", "-"),
                    url=f"{self.url}/build",
                    build_date="2019-11-15",
                    build_status="failed",
                )
            ],
        )

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned, that pipelines can be included and ignored by name and by
        regular expression."""
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["include.*"]
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["include_but_ignore_by_name", "folder/.*ignore.*"]
        metric = dict(type="unused_jobs", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(
                        path=self.path,
                        name="include_pipeline",
                        _links=dict(web=dict(href=f"{self.url}/build")),
                        latestCompletedBuild=dict(result="failed", finishTime="2019-10-15T12:24:10.1905868Z"),
                    ),
                    dict(path=self.path, name="include_but_ignore_by_re", latestCompletedBuild=dict(result="failed")),
                    dict(path=self.path, name="dont_include_by_re", latestCompletedBuild=dict(result="failed")),
                    dict(path=r"\\", name="include_but_ignore_by_name", latestCompletedBuild=dict(result="failed")),
                ]
            ),
        )
        self.assert_measurement(
            response,
            value="1",
            landing_url=f"{self.url}/_build",
            api_url=self.api_url,
            entities=[
                dict(
                    name=self.pipeline,
                    key=self.pipeline.replace("/", "-"),
                    url=f"{self.url}/build",
                    build_date="2019-10-15",
                    build_status="failed",
                )
            ],
        )
