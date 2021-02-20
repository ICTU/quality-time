"""Unit tests for the Azure Devops Server unused jobs collectors."""

from .base import AzureDevopsJobsTestCase


class AzureDevopsUnusedJobsTest(AzureDevopsJobsTestCase):
    """Unit tests for the Azure Devops Server unused jobs collector."""

    METRIC_TYPE = "unused_jobs"

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned.

        Also test that pipelines can be included and ignored by name and by regular expression.
        """
        self.set_source_parameter("jobs_to_include", ["include.*"])
        self.set_source_parameter("jobs_to_ignore", ["include_but_ignore_by_name", "folder/.*ignore.*"])
        response = await self.collect(self.metric, get_request_json_return_value=dict(value=self.jobs))
        self.assert_measurement(
            response, value="1", landing_url=self.landing_url, api_url=self.api_url, entities=self.expected_entities
        )
