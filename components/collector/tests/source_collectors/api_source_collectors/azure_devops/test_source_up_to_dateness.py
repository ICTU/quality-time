"""Unit tests for the Azure Devops Server source up-to-dateness collector."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago

from .base import AzureDevopsTestCase


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
