"""Unit tests for the Azure Devops Server failed jobs collectors."""

from .base import AzureDevopsJobsTestCase


class AzureDevopsFailedJobsTest(AzureDevopsJobsTestCase):
    """Unit tests for the Azure Devops Server failed jobs collector."""

    METRIC_TYPE = "failed_jobs"

    async def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned.

        Also test that pipelines can be included and ignored by status, by name, and by regular expression.
        """
        self.sources["source_id"]["parameters"]["failure_type"] = ["failed"]
        self.sources["source_id"]["parameters"]["jobs_to_include"] = ["include.*"]
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["include_but_ignore_by_name", "folder/.*ignore.*"]
        response = await self.collect(
            self.metric,
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
