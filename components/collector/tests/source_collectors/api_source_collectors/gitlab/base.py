"""GitLab unit test base classes."""

from ...source_collector_test_case import SourceCollectorTestCase


class GitLabTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing GitLab collectors."""

    def setUp(self):
        """Extend to add generic test fixtures."""
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="gitlab",
                parameters=dict(
                    url="https://gitlab/",
                    project="namespace/project",
                    file_path="file",
                    branch="branch",
                    inactive_days="7",
                    branches_to_ignore=["ignored_.*"],
                ),
            )
        )
        self.gitlab_jobs_json = [
            dict(
                id="1",
                status="failed",
                name="job1",
                stage="stage",
                created_at="2019-03-31T19:50:39.927Z",
                web_url="https://gitlab/job1",
                ref="master",
            ),
            dict(
                id="2",
                status="failed",
                name="job2",
                stage="stage",
                created_at="2019-03-31T19:50:39.927Z",
                web_url="https://gitlab/job2",
                ref="develop",
            ),
        ]
        self.expected_entities = [
            dict(
                key="1",
                name="job1",
                stage="stage",
                branch="master",
                url="https://gitlab/job1",
                build_date="2019-03-31",
                build_status="failed",
            ),
            dict(
                key="2",
                name="job2",
                stage="stage",
                branch="develop",
                url="https://gitlab/job2",
                build_date="2019-03-31",
                build_status="failed",
            ),
        ]


class CommonGitLabJobsTestsMixin:
    """Unit tests that should succeed for both the unused jobs metric as well as the failed jobs metric."""

    async def test_ignore_job_by_name(self):
        """Test that jobs can be ignored by name."""
        self.sources["source_id"]["parameters"]["jobs_to_ignore"] = ["job2"]
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:-1])

    async def test_ignore_job_by_ref(self):
        """Test that jobs can be ignored by ref."""
        self.sources["source_id"]["parameters"]["refs_to_ignore"] = ["develop"]
        response = await self.collect(self.metric, get_request_json_return_value=self.gitlab_jobs_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:-1])
