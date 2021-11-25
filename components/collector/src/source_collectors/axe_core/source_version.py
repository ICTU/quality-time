"""Axe-core accessibility source version collector."""

from packaging.version import Version

from base_collectors import JSONFileSourceCollector, SourceVersionCollector
from collector_utilities.type import Response


class AxeCoreSourceVersion(JSONFileSourceCollector, SourceVersionCollector):
    """Collector to get the version of Axe-core from its JSON reports."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the response."""
        json = await response.json(content_type=None)
        if isinstance(json, list):
            json = json[0]  # The JSON consists of several Axe-core JSONs in a list, assume they have the same version
        return Version(json["testEngine"]["version"])
