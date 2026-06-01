"""GitHub collector base classes."""

from abc import ABC

from base_collectors import TokenAuthenticationSourceCollector


class GitHubBase(TokenAuthenticationSourceCollector, ABC):
    """Base class for GitHub collectors."""

    AUTH_PREFIX = "bearer "
