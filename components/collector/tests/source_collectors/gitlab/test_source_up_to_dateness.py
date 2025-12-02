"""Unit tests for the GitLab source up-to-dateness collector."""

from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock, _patch, patch

from aiohttp import ClientResponseError, RequestInfo
from aiohttp.client_reqrep import URL, CIMultiDict, CIMultiDictProxy
from dateutil.tz import tzutc

from collector_utilities.date_time import days_ago, parse_datetime

from .base import FakeResponse, GitLabTestCase


class GitLabSourceUpToDatenessTest(GitLabTestCase):
    """Unit tests for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.commit_json = {"committed_date": "2019-01-01T09:06:12+00:00"}
        self.expected_age = days_ago(datetime(2019, 1, 1, 9, 6, 12, tzinfo=tzutc()))

    @staticmethod
    def patched_client_session_head(*responses: ClientResponseError) -> _patch[AsyncMock]:
        """Return a patched version of the client session head method."""
        head_response = Mock(headers={"X-Gitlab-Last-Commit-Id": "commit-sha"})
        head_responses = responses or [head_response, head_response]
        return patch("aiohttp.ClientSession.head", AsyncMock(side_effect=head_responses))

    @staticmethod
    def client_response_error(status: int) -> ClientResponseError:
        """Create a client response error with the given status code."""
        request_info = RequestInfo(URL("https://gitlab.com/irrelevant"), "GET", headers=CIMultiDictProxy(CIMultiDict()))
        return ClientResponseError(request_info, history=(), status=status)

    async def test_source_up_to_dateness_file(self):
        """Test that the age of a file in a repo can be measured."""
        not_found = self.client_response_error(HTTPStatus.NOT_FOUND)
        with self.patched_client_session_head():
            response = await self.collect(
                get_request_json_side_effect=[not_found, self.commit_json, {"web_url": "https://gitlab.com/project"}],
            )
        self.assert_measurement(
            response,
            value=str(self.expected_age),
            landing_url="https://gitlab.com/project/blob/branch/file",
        )

    async def test_source_up_to_dateness_non_existing_file(self):
        """Test that the age of a non-existing file in a repo cannot be measured."""
        not_found = self.client_response_error(HTTPStatus.NOT_FOUND)
        with self.patched_client_session_head(not_found):
            response = await self.collect(get_request_json_side_effect=[not_found])
        self.assert_measurement(response, connection_error="404", landing_url="https://gitlab")

    async def test_source_up_to_dateness_internal_server_error(self):
        """Test that the age of a file in a repo cannot be measured if GitLab returns a server error."""
        server_error = self.client_response_error(HTTPStatus.INTERNAL_SERVER_ERROR)
        with self.patched_client_session_head():
            response = await self.collect(get_request_json_side_effect=[server_error])
        self.assert_measurement(response, connection_error="500", landing_url="https://gitlab")

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
                "id": "id",
                "project_id": "project_id",
                "name": "Pipeline name",
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
            response = await self.collect(
                get_request_side_effect=[
                    FakeResponse([]),  # No pipeline schedules
                    FakeResponse(pipeline_json),
                ]
            )
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
            mock_dt.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=tzutc())
            response = await self.collect(get_request_json_side_effect=[ConnectionError])
        api_url = "https://gitlab/api/v4/projects/namespace%2Fproject/pipelines?updated_after=2023-12-25&per_page=100"
        self.assert_measurement(response, landing_url=api_url, connection_error="Traceback")
