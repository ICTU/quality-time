"""Base class for Azure DevOps unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Azure DevOps collectors."""

    SOURCE_TYPE = "azure_devops"

    def setUp(self):
        """Extend to add Azure DevOps fixtures."""
        super().setUp()
        self.url = "https://azure_devops/org/project"
        self.work_item_url = "https://work_item"
        self.set_source_parameter("url", self.url)
        self.set_source_parameter("wiql", "wiql")
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


class AzureDevopsJobsTestCase(AzureDevopsTestCase):  # skipcq: PTC-W0046
    """Base class for Azure DevOps jobs collectors."""

    def setUp(self):
        """Extend to set up job data."""
        super().setUp()
        self.path = r"\\folder"
        self.pipeline = r"folder/include_pipeline"
        self.api_url = f"{self.url}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1"
        self.landing_url = f"{self.url}/_build"
        self.jobs = [
            dict(
                path=self.path,
                name="include_pipeline",
                _links=dict(web=dict(href=f"{self.url}/build")),
                latestCompletedBuild=dict(result="failed", finishTime="2019-10-15T12:24:10.1905868Z"),
            ),
            dict(path=self.path, name="no_completed_builds"),
            dict(path=self.path, name="include_but_ignore_by_re", latestCompletedBuild=dict(result="failed")),
            dict(path=self.path, name="dont_include_by_re", latestCompletedBuild=dict(result="failed")),
            dict(path=r"\\", name="include_but_ignore_by_name", latestCompletedBuild=dict(result="failed")),
        ]
        self.expected_entities = [
            dict(
                name=self.pipeline,
                key=self.pipeline.replace("/", "-"),
                url=f"{self.url}/build",
                build_date="2019-10-15",
                build_status="failed",
            )
        ]


class AzureDevopsPipelinesTestCase(AzureDevopsTestCase):  # skipcq: PTC-W0046
    """Base class for Azure DevOps pipeline collectors."""

    def setUp(self):
        """Extend to set up pipeline data."""
        super().setUp()
        self.pipelines = dict(count=1, value=[dict(id=42, name="azure-pipelines.yml")])
        self.pipeline_runs = dict(
            count=3,
            value=[
                dict(
                    state="completed",
                    result="succeeded",
                    createdDate="2019-10-15T12:20:10.1905868Z",
                    finishedDate="2019-10-15T12:24:10.1905868Z",
                    id=1,
                    name="20191015.1",
                    url=f"{self.url}/_build/results?buildId=1",
                    _links=dict(web=dict(href=f"{self.url}/_build/results?buildId=1")),
                ),
                dict(
                    state="completed",
                    result="succeeded",
                    createdDate="2019-10-15T12:30:10.1905868Z",
                    finishedDate="2019-10-15T12:34:10.1905868Z",
                    id=2,
                    name="20191015.2",
                    url=f"{self.url}/_build/results?buildId=2",
                    _links=dict(web=dict(href=f"{self.url}/_build/results?buildId=2")),
                ),
                dict(
                    state="inProgress",
                    createdDate="2019-10-15T12:40:10.1905868Z",
                    id=4,
                    name="20191015.4",
                    url=f"{self.url}/_build/results?buildId=4",
                    _links=dict(web=dict(href=f"{self.url}/_build/results?buildId=4")),
                )
            ]
        )
        self.expected_entities = [
            dict(
                name="20191015.1",
                key=f"{self.pipelines['value'][0]['id']}-20191015_1",  # safe_entity_key
                url=f"{self.url}/_build/results?buildId=1",
                build_date="2019-10-15",
                build_status="completed",
            ),
            dict(
                name="20191015.2",
                key=f"{self.pipelines['value'][0]['id']}-20191015_2",  # safe_entity_key
                url=f"{self.url}/_build/results?buildId=2",
                build_date="2019-10-15",
                build_status="completed",
            )
        ]
