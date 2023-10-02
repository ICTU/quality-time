"""Base class for Azure DevOps unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):
    """Base class for testing Azure DevOps collectors."""

    SOURCE_TYPE = "azure_devops"

    def setUp(self):
        """Extend to add Azure DevOps fixtures."""
        super().setUp()
        self.url = "https://azure_devops/org/project"
        self.work_item_url = "https://work_item"
        self.set_source_parameter("url", self.url)
        self.work_item = {
            "id": "id",
            "_links": {"html": {"href": self.work_item_url}},
            "fields": {
                "System.TeamProject": "Project",
                "System.Title": "Title",
                "System.WorkItemType": "Task",
                "System.State": "New",
                "Microsoft.VSTS.Scheduling.Effort": 2.0,
            },
        }


class AzureDevopsJobsTestCase(AzureDevopsTestCase):
    """Base class for Azure DevOps jobs collectors."""

    def setUp(self):
        """Extend to set up job data."""
        super().setUp()
        self.path = r"\\folder"
        self.pipeline = r"folder/include_pipeline"
        self.api_url = f"{self.url}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1"
        self.landing_url = f"{self.url}/_build"
        self.jobs = [
            {
                "path": self.path,
                "name": "include_pipeline",
                "_links": {"web": {"href": f"{self.url}/build"}},
                "latestCompletedBuild": {"result": "failed", "finishTime": "2019-10-15T12:24:10.1905868Z"},
            },
            {
                "path": self.path,
                "name": "no_completed_builds",
                "_links": {"web": {"href": f"{self.url}/build"}},
            },
            {
                "path": self.path,
                "name": "include_but_ignore_by_re",
                "_links": {"web": {"href": f"{self.url}/build"}},
                "latestCompletedBuild": {"result": "failed"},
            },
            {
                "path": self.path,
                "name": "dont_include_by_re",
                "_links": {"web": {"href": f"{self.url}/build"}},
                "latestCompletedBuild": {"result": "failed"},
            },
            {
                "path": r"\\",
                "name": "include_but_ignore_by_name",
                "_links": {"web": {"href": f"{self.url}/build"}},
                "latestCompletedBuild": {"result": "failed"},
            },
        ]
        self.expected_entities = [
            {
                "name": self.pipeline,
                "key": self.pipeline.replace("/", "-"),
                "url": f"{self.url}/build",
                "build_date": "2019-10-15",
                "build_status": "failed",
            },
        ]


class AzureDevopsPipelinesTestCase(AzureDevopsTestCase):
    """Base class for Azure DevOps pipeline collectors."""

    def setUp(self):
        """Extend to set up pipeline data."""
        super().setUp()
        self.test_pipeline = {"id": 42, "name": "azure-pipelines.yml"}
        self.pipelines = {"count": 1, "value": [self.test_pipeline]}
        self.pipeline_runs = {
            "count": 3,
            "value": [
                {
                    "state": "completed",
                    "result": "succeeded",
                    "createdDate": "2019-10-15T12:20:10.1905868Z",
                    "finishedDate": "2019-10-15T12:24:10.1905868Z",
                    "pipeline": self.test_pipeline,
                    "id": 1,
                    "name": "20191015.1",
                    "url": f"{self.url}/_build/results?buildId=1",
                    "_links": {"web": {"href": f"{self.url}/_build/results?buildId=1"}},
                },
                {
                    "state": "completed",
                    "result": "succeeded",
                    "createdDate": "2019-10-15T12:30:10.1905868Z",
                    "finishedDate": "2019-10-15T12:34:10.1905868Z",
                    "pipeline": self.test_pipeline,
                    "id": 2,
                    "name": "20191015.2",
                    "url": f"{self.url}/_build/results?buildId=2",
                    "_links": {"web": {"href": f"{self.url}/_build/results?buildId=2"}},
                },
                {
                    "state": "inProgress",
                    "createdDate": "2019-10-15T12:40:10.1905868Z",
                    "pipeline": self.test_pipeline,
                    "id": 4,
                    "name": "20191015.4",
                    "url": f"{self.url}/_build/results?buildId=4",
                    "_links": {"web": {"href": f"{self.url}/_build/results?buildId=4"}},
                },
            ],
        }
        self.expected_entities = [
            {
                "name": "20191015.1",
                "pipeline": self.test_pipeline["name"],
                "key": f"{self.test_pipeline['id']}-20191015_1",  # safe_entity_key
                "url": f"{self.url}/_build/results?buildId=1",
                "build_date": "2019-10-15",
                "build_status": "completed",
            },
            {
                "name": "20191015.2",
                "pipeline": self.test_pipeline["name"],
                "key": f"{self.test_pipeline['id']}-20191015_2",  # safe_entity_key
                "url": f"{self.url}/_build/results?buildId=2",
                "build_date": "2019-10-15",
                "build_status": "completed",
            },
        ]
