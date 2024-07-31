"""Github collector base classes."""

from abc import ABC

from base_collectors import SourceCollector


class GitHubBase(SourceCollector, ABC):
    """Base class for GitHub collectors."""

    def _headers(self) -> dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Authorization"] = "bearer " + str(private_token)
        return headers
