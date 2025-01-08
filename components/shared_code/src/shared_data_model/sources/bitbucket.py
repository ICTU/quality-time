"""Bitbucket source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    BranchesToIgnore,
    BranchMergeStatus,
    Days,
    PrivateToken,
    StringParameter,
)

BITBUCKET_BRANCH_HELP_URL = HttpUrl("https://confluence.atlassian.com/bitbucketserver/branches-776639968.html")

BITBUCKET = Source(
    name="Bitbucket",
    description="Bitbucket is a Git-based source code hosting and collaboration tool, built for teams.",
    url=HttpUrl("https://bitbucket.org/product/guides/getting-started/overview#a-brief-overview-of-bitbucket/"),
    documentation={},
    parameters={
        "url": URL(
            name="Bitbucket instance URL",
            help="URL of the Bitbucket instance, with port if necessary, but without path. For example, "
            "'https://bitbucket.org'.",
            validate_on=["private_token"],
            metrics=["inactive_branches"],
        ),
        "owner": StringParameter(
            name="Owner (name of owner of the repository)",
            short_name="owner",
            mandatory=True,
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-project/"),
            metrics=["inactive_branches"],
        ),
        "repository": StringParameter(
            name="Repository (name of the repository)",
            short_name="repository",
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-git-repository/"),
            mandatory=True,
            metrics=["inactive_branches"],
        ),
        "private_token": PrivateToken(
            name="Private token (with read_api scope)",
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-repository-access-token/"),
            metrics=["inactive_branches"],
        ),
        "branches_to_ignore": BranchesToIgnore(help_url=BITBUCKET_BRANCH_HELP_URL),
        "branch_merge_status": BranchMergeStatus(),
        "inactive_days": Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["inactive_branches"],
        ),
    },
    entities={
        "inactive_branches": Entity(
            name="branch",
            name_plural="branches",
            attributes=[
                EntityAttribute(name="Branch name", key="name", url="url"),
                EntityAttribute(
                    name="Date of most recent commit",
                    key="commit_date",
                    type=EntityAttributeType.DATE,
                ),
                EntityAttribute(name="Merge status"),
            ],
        )
    },
)
