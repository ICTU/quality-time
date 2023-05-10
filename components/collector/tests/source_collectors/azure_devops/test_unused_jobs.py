"""Unit tests for the Azure DevOps Server unused jobs collectors."""

from .base import AzureDevopsJobsTestCase


class AzureDevopsUnusedJobsTest(AzureDevopsJobsTestCase):
    """Unit tests for the Azure DevOps Server unused jobs collector."""

    METRIC_TYPE = "unused_jobs"

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned.

        Also test that pipelines can be included and ignored by name and by regular expression.
        """
        self.set_source_parameter("jobs_to_include", ["folder/include.*"])
        self.set_source_parameter("jobs_to_ignore", ["folder/include_but_ignore_by_name", "folder/.*ignore.*"])
        response = await self.collect(get_request_json_return_value={"value": self.jobs})
        self.assert_measurement(
            response,
            value="1",
            landing_url=self.landing_url,
            api_url=self.api_url,
            entities=self.expected_entities,
        )

    async def test_no_jobs_without_build_date(self):
        """Test that unused jobs without build_date are not returned."""
        self.set_source_parameter("jobs_to_include", ["folder/include_but_ignore_by_re"])
        response = await self.collect(get_request_json_return_value={"value": self.jobs})
        self.assert_measurement(response, value="0", landing_url=self.landing_url, api_url=self.api_url, entities=[])
