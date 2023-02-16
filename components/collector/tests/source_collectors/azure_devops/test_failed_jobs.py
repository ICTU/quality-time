"""Unit tests for the Azure DevOps Server failed jobs collectors."""

from .base import AzureDevopsJobsTestCase


class AzureDevopsFailedJobsTest(AzureDevopsJobsTestCase):
    """Unit tests for the Azure DevOps Server failed jobs collector."""

    METRIC_TYPE = "failed_jobs"

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned.

        Also test that pipelines can be included and ignored by status, by name, and by regular expression.
        """
        self.set_source_parameter("failure_type", ["failed"])
        self.set_source_parameter("jobs_to_include", ["folder/include.*"])
        self.set_source_parameter("jobs_to_ignore", ["folder/include_but_ignore_by_name", "folder/.*ignore.*"])
        response = await self.collect(
            get_request_json_return_value=dict(
                value=self.jobs
                + [
                    dict(
                        path=rf"{self.path}\\subfolder",
                        name="include_pipeline",
                        latestCompletedBuild=dict(result="canceled"),
                        _links=dict(web=dict(href=f"{self.url}/build")),
                    ),
                ]
            )
        )
        self.assert_measurement(
            response, value="1", landing_url=self.landing_url, api_url=self.api_url, entities=self.expected_entities
        )
