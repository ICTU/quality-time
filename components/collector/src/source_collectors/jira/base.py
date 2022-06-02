"""Base classes for Jira collectors."""

from base_collectors import SourceCollector


class JiraBase(SourceCollector):
    """Base class for Jira collectors."""

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Extend to only return the basic auth credentials if no private token is configured.

        This prevents aiohttp from complaining that it "Cannot combine AUTHORIZATION header with AUTH argument or
        credentials encoded in URL".
        """
        return None if self._parameter("private_token") else super()._basic_auth_credentials()

    def _headers(self) -> dict[str, str]:
        """Extend to add the token, if present, to the headers for the get request."""
        headers = super()._headers()
        if token := self._parameter("private_token"):
            headers["Authorization"] = f"Bearer {token}"
        return headers
