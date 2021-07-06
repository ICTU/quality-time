"""Unit tests for the GitLab unmerged branches collector."""

from datetime import datetime, timezone

from .base import GitLabTestCase


class GitLabUnmergedBranchesTest(GitLabTestCase):
    """Unit tests for the unmerged branches metric."""

    METRIC_TYPE = "unmerged_branches"

    def setUp(self):
        """Extend to setup fixtures."""
        super().setUp()
        self.set_source_parameter("branches_to_ignore", ["ignored_.*"])
        self.main = dict(name="main", default=True, merged=False)
        self.unmerged = dict(
            name="unmerged_branch",
            default=False,
            merged=False,
            web_url="https://gitlab/namespace/project/-/tree/unmerged_branch",
            commit=dict(committed_date="2019-04-02T11:33:04.000+02:00"),
        )
        self.ignored = dict(
            name="ignored_branch",
            default=False,
            merged=False,
            commit=dict(committed_date="2019-04-02T11:33:04.000+02:00"),
        )
        self.active_unmerged = dict(
            name="active_unmerged_branch",
            default=False,
            merged=False,
            commit=dict(committed_date=datetime.now(timezone.utc).isoformat()),
        )
        self.merged = dict(name="merged_branch", default=False, merged=True)
        self.expected_entities = [
            dict(
                key="unmerged_branch",
                name="unmerged_branch",
                commit_date="2019-04-02",
                url="https://gitlab/namespace/project/-/tree/unmerged_branch",
            )
        ]
        self.landing_url = "https://gitlab/namespace/project/-/branches"

    async def test_unmerged_branches(self):
        """Test that the number of unmerged branches can be measured."""
        branches = [self.main, self.unmerged, self.ignored, self.active_unmerged, self.merged]
        response = await self.collect(get_request_json_return_value=branches)
        self.assert_measurement(response, value="1", entities=self.expected_entities, landing_url=self.landing_url)

    async def test_unmerged_branches_paginated(self):
        """Test that pagination works."""
        branches = [[self.main, self.merged, self.ignored], [self.merged, self.unmerged]]
        links = dict(next=dict(url="https://gitlab/next_page"))
        response = await self.collect(get_request_json_side_effect=branches, get_request_links=links)
        self.assert_measurement(response, value="1", entities=self.expected_entities, landing_url=self.landing_url)
