"""Unit tests for the GitLab source up-to-dateness collector."""

from datetime import datetime, date, timezone
from unittest.mock import AsyncMock, Mock, patch

from .base import GitLabTestCase


class GitLabSourceUpToDatenessTest(GitLabTestCase):
    """Unit tests for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.commit_json = dict(committed_date="2019-01-01T09:06:12+00:00")
        self.expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.head_response = Mock()
        self.head_response.headers = {"X-Gitlab-Last-Commit-Id": "commit-sha"}

    async def test_source_up_to_dateness_file(self):
        """Test that the age of a file in a repo can be measured."""
        with patch("aiohttp.ClientSession.head", AsyncMock(return_value=self.head_response)):
            response = await self.collect(
                get_request_json_side_effect=[[], self.commit_json, dict(web_url="https://gitlab.com/project")]
            )
        self.assert_measurement(
            response, value=str(self.expected_age), landing_url="https://gitlab.com/project/blob/branch/file"
        )

    async def test_source_up_to_dateness_folder(self):
        """Test that the age of a folder in a repo can be measured."""
        with patch("aiohttp.ClientSession.head", AsyncMock(side_effect=[self.head_response, self.head_response])):
            response = await self.collect(
                get_request_json_side_effect=[
                    [dict(type="blob", path="file.txt"), dict(type="tree", path="folder")],
                    [dict(type="blob", path="file.txt")],
                    self.commit_json,
                    self.commit_json,
                    dict(web_url="https://gitlab.com/project"),
                ]
            )
        self.assert_measurement(
            response, value=str(self.expected_age), landing_url="https://gitlab.com/project/blob/branch/file"
        )

    async def test_source_up_to_dateness_pipeline(self):
        """Test that the age of a pipeline can be measured."""
        self.set_source_parameter("file_path", "")
        build_date = datetime.fromisoformat(self.gitlab_jobs_json[0]["created_at"].strip("Z")).date()
        expected_age = (date.today() - build_date).days
        with patch("aiohttp.ClientSession.head", AsyncMock(return_value=self.head_response)):
            response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value=str(expected_age), landing_url="https://gitlab/project/-/pipelines/1")

    async def test_file_landing_url_on_failure(self):
        """Test that the landing url is the API url when GitLab cannot be reached."""
        response = await self.collect(get_request_json_side_effect=[ConnectionError])
        self.assert_measurement(response, landing_url="https://gitlab", connection_error="Traceback")

    async def test_pipeline_landing_url_on_failure(self):
        """Test that the landing url is the API url when GitLab cannot be reached."""
        self.set_source_parameter("file_path", "")
        response = await self.collect(get_request_json_side_effect=[ConnectionError])
        self.assert_measurement(response, landing_url="https://gitlab", connection_error="Traceback")
