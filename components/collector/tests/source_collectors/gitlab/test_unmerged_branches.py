"""Unit tests for the GitLab unmerged branches collector."""

from datetime import datetime, UTC

from .base import GitLabTestCase


class GitLabUnmergedBranchesTest(GitLabTestCase):
    """Unit tests for the unmerged branches metric."""

    METRIC_TYPE = "unmerged_branches"

    def setUp(self):
        """Extend to setup fixtures."""
        super().setUp()
        self.set_source_parameter("branches_to_ignore", ["ignored_.*"])
        self.main = {"name": "main", "default": True, "merged": False}
        self.unmerged = {
            "name": "unmerged_branch",
            "default": False,
            "merged": False,
            "web_url": "https://gitlab/namespace/project/-/tree/unmerged_branch",
            "commit": {"committed_date": "2019-04-02T11:33:04.000+02:00"},
        }
        self.ignored = {
            "name": "ignored_branch",
            "default": False,
            "merged": False,
            "commit": {"committed_date": "2019-04-02T11:33:04.000+02:00"},
        }
        self.active_unmerged = {
            "name": "active_unmerged_branch",
            "default": False,
            "merged": False,
            "commit": {"committed_date": datetime.now(tz=UTC).isoformat()},
        }
        self.merged = {"name": "merged_branch", "default": False, "merged": True}
        self.expected_entities = [
            {
                "key": "unmerged_branch",
                "name": "unmerged_branch",
                "commit_date": "2019-04-02",
                "url": "https://gitlab/namespace/project/-/tree/unmerged_branch",
            },
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
        links = {"next": {"url": "https://gitlab/next_page"}}
        response = await self.collect(get_request_json_side_effect=branches, get_request_links=links)
        self.assert_measurement(response, value="1", entities=self.expected_entities, landing_url=self.landing_url)
