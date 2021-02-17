"""Unit tests for the Azure Devops Server unused jobs collectors."""

from .base import AzureDevopsTestCase


class AzureDevopsUnusedJobsTest(AzureDevopsTestCase):
    """Unit tests for the Azure Devops Server unused jobs collector."""

    METRIC_TYPE = "unused_jobs"

    def setUp(self):
        """Extend to set up test fixtures."""
        super().setUp()
        self.path = r"\\folder"
        self.pipeline = r"folder/include_pipeline"
        self.api_url = f"{self.url}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1"

    async def test_nr_of_unused_jobs(self):
        """Test that the number of unused jobs is returned.

        Also test that pipelines can be included and ignored by name and by regular expression.
        """
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
