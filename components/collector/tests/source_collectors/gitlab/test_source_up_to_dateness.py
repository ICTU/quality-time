"""Unit tests for the GitLab source up-to-dateness collector."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, _patch, patch

from collector_utilities.date_time import days_ago, parse_datetime

from .base import GitLabTestCase


class GitLabSourceUpToDatenessTest(GitLabTestCase):
    """Unit tests for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.commit_json = {"committed_date": "2019-01-01T09:06:12+00:00"}
        self.expected_age = days_ago(datetime(2019, 1, 1, 9, 6, 12, tzinfo=UTC))

    @staticmethod
    def patched_client_session_head() -> _patch[AsyncMock]:
        """Return a patched version of the client session head method."""
        head_response = Mock(headers={"X-Gitlab-Last-Commit-Id": "commit-sha"})
        return patch("aiohttp.ClientSession.head", AsyncMock(side_effect=[head_response, head_response]))

    async def test_source_up_to_dateness_file(self):
        """Test that the age of a file in a repo can be measured."""
        with self.patched_client_session_head():
            response = await self.collect(
                get_request_json_side_effect=[[], self.commit_json, {"web_url": "https://gitlab.com/project"}],
            )
        self.assert_measurement(
            response,
            value=str(self.expected_age),
            landing_url="https://gitlab.com/project/blob/branch/file",
        )

    async def test_source_up_to_dateness_folder(self):
        """Test that the age of a folder in a repo can be measured."""
        with self.patched_client_session_head():
            response = await self.collect(
                get_request_json_side_effect=[
                    [{"type": "blob", "path": "file.txt"}, {"type": "tree", "path": "folder"}],
                    [{"type": "blob", "path": "file.txt"}],
                    self.commit_json,
                    self.commit_json,
                    {"web_url": "https://gitlab.com/project"},
                ],
            )
        self.assert_measurement(
            response,
            value=str(self.expected_age),
            landing_url="https://gitlab.com/project/blob/branch/file",
        )

    async def test_source_up_to_dateness_pipeline(self):
        """Test that the age of a pipeline can be measured."""
        self.set_source_parameter("file_path", "")
        pipeline_json = [
            {
                "created_at": "2020-11-24T10:00:00Z",
                "updated_at": "2020-11-24T10:00:00Z",
                "ref": "branch",
                "status": "success",
                "source": "push",
                "web_url": "https://gitlab/project/-/pipelines/1",
            },
        ]
        expected_age = days_ago(parse_datetime(pipeline_json[0]["updated_at"]))
        with self.patched_client_session_head():
            response = await self.collect(get_request_json_return_value=pipeline_json)
        self.assert_measurement(response, value=str(expected_age), landing_url="https://gitlab/project/-/pipelines/1")

    async def test_source_up_to_dateness_pipeline_missing(self):
        """Test that the age of a pipeline results in an error message if no pipeline can be found."""
        self.set_source_parameter("file_path", "")
        with self.patched_client_session_head():
            response = await self.collect(get_request_json_return_value=[])
        self.assert_measurement(response, value=None, parse_error="No pipelines found within the lookback period")

    async def test_file_landing_url_on_failure(self):
        """Test that the landing url is the API url when GitLab cannot be reached."""
        response = await self.collect(get_request_json_side_effect=[ConnectionError])
        self.assert_measurement(response, landing_url="https://gitlab", connection_error="Traceback")

    async def test_pipeline_landing_url_on_failure(self):
        """Test that the landing url is the API url when GitLab cannot be reached."""
        self.set_source_parameter("file_path", "")
        with patch("shared.utils.date_time.datetime", wraps=datetime) as mock_dt:
            mock_dt.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
            response = await self.collect(get_request_json_side_effect=[ConnectionError])
        api_url = "https://gitlab/api/v4/projects/namespace%2Fproject/pipelines?updated_after=2023-12-25&per_page=100"
        self.assert_measurement(response, landing_url=api_url, parse_error="Traceback")
