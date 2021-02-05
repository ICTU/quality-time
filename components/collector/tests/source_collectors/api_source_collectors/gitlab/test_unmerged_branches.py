"""Unit tests for the GitLab unmerged branches collector."""

from datetime import datetime, timezone

from .base import GitLabTestCase


class GitLabUnmergedBranchesTest(GitLabTestCase):
    """Unit tests for the unmerged branches metric."""

    async def test_unmerged_branches(self):
        """Test that the number of unmerged branches can be measured."""
        metric = dict(type="unmerged_branches", sources=self.sources, addition="sum")
        gitlab_json = [
            dict(name="master", default=True, merged=False),
            dict(
                name="unmerged_branch",
                default=False,
                merged=False,
                web_url="https://gitlab/namespace/project/-/tree/unmerged_branch",
                commit=dict(committed_date="2019-04-02T11:33:04.000+02:00"),
            ),
            dict(
                name="ignored_branch",
                default=False,
                merged=False,
                commit=dict(committed_date="2019-04-02T11:33:04.000+02:00"),
            ),
            dict(
                name="active_unmerged_branch",
                default=False,
                merged=False,
                commit=dict(committed_date=datetime.now(timezone.utc).isoformat()),
            ),
            dict(name="merged_branch", default=False, merged=True),
        ]
        response = await self.collect(metric, get_request_json_return_value=gitlab_json)
        expected_entities = [
            dict(
                key="unmerged_branch",
                name="unmerged_branch",
                commit_date="2019-04-02",
                url="https://gitlab/namespace/project/-/tree/unmerged_branch",
            )
        ]
        self.assert_measurement(
            response, value="1", entities=expected_entities, landing_url="https://gitlab/namespace/project/-/branches"
        )
