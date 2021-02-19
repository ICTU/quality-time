"""Base class for Azure Devops unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Azure DevOps collectors."""

    SOURCE_TYPE = "azure_devops"

    def setUp(self):
        """Extend to add Azure DevOps fixtures."""
        super().setUp()
        self.url = "https://azure_devops/org/project"
        self.work_item_url = "https://work_item"
        self.sources["source_id"]["parameters"]["url"] = self.url
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


class AzureDevopsJobsTestCase(AzureDevopsTestCase):
    """Base class for Azure Devops jobs collectors."""

    def setUp(self):
        """Extend to set up job data."""
        super().setUp()
        self.path = r"\\folder"
        self.pipeline = r"folder/include_pipeline"
        self.api_url = f"{self.url}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1"
