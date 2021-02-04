"""GitLab unit test base classes."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GitLabTestCase(SourceCollectorTestCase):
    """Base class for testing GitLab collectors."""

    def setUp(self):
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
