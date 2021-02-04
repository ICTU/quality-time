"""Base class for Azure Devops unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class AzureDevopsTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
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
