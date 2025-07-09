"""GitLab unit test base classes."""

from datetime import datetime

from dateutil.tz import tzutc

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class FakeResponse:
    """Fake GitLab response."""

    def __init__(self, fake_json, links=None) -> None:
        self.fake_json = fake_json
        self.links = links or {}

    async def json(self):
        """Return the fake JSON."""
        return self.fake_json

    async def read(self):
        """Fake a read method."""


class GitLabTestCase(SourceCollectorTestCase):
    """Base class for testing GitLab collectors."""

    SOURCE_TYPE = "gitlab"
    LOOKBACK_DAYS = "100000"

    def setUp(self):
        """Extend to add generic test fixtures."""
        super().setUp()
        self.set_source_parameter("branch", "branch")
        self.set_source_parameter("file_path", "file")
        self.set_source_parameter("lookback_days", self.LOOKBACK_DAYS)
        self.set_source_parameter("project", "namespace/project")
        self.gitlab_jobs_json = [
            {
                "id": "1",
                "status": "skipped",
                "name": "job1",
                "stage": "stage",
                "created_at": "2019-03-31T19:40:39.927Z",
                "pipeline": {"web_url": "https://gitlab/project/-/pipelines/1"},
                "web_url": "https://gitlab/job1",
                "ref": "main",
            },
            {
                "id": "2",
                "status": "failed",
                "name": "job2",
                "stage": "stage",
                "created_at": "2019-03-31T19:40:39.927Z",
                "web_url": "https://gitlab/job2",
                "ref": "develop",
            },
        ]
        self.expected_entities = [
            {
                "key": "1",
                "name": "job1",
                "stage": "stage",
                "branch": "main",
                "url": "https://gitlab/job1",
                "build_date": "2019-03-31",
                "build_datetime": datetime(2019, 3, 31, 19, 40, 39, 927000, tzinfo=tzutc()),
                "build_result": "skipped",
            },
            {
                "key": "2",
                "name": "job2",
                "stage": "stage",
                "branch": "develop",
                "url": "https://gitlab/job2",
                "build_date": "2019-03-31",
                "build_datetime": datetime(2019, 3, 31, 19, 40, 39, 927000, tzinfo=tzutc()),
                "build_result": "failed",
            },
        ]


class GitLabJobsTestCase(GitLabTestCase):
    """Base class for GitLab job collector unit tests."""

    LANDING_URL = "https://gitlab/namespace/project/-/jobs"


class CommonGitLabJobsTestsMixin:
    """Unit tests that should succeed for both the unused jobs metric as well as the failed jobs metric."""

    async def test_ignore_job_by_name(self):
        """Test that jobs can be ignored by name."""
        self.set_source_parameter("jobs_to_ignore", ["job2"])
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:-1])

    async def test_include_job_by_name(self):
        """Test that jobs can be included by name."""
        self.set_source_parameter("jobs_to_include", ["job1"])
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:-1])

    async def test_ignore_job_by_ref(self):
        """Test that jobs can be ignored by ref."""
        self.set_source_parameter("refs_to_ignore", ["develop"])
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:-1])

    async def test_include_job_by_ref(self):
        """Test that jobs can be included by ref."""
        self.set_source_parameter("refs_to_include", ["main"])
        response = await self.collect(get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:-1])
