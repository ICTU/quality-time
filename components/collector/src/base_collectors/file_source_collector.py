"""File source collector base classes."""

import asyncio
import io
import itertools
import json
import zipfile
from abc import ABC
from http import HTTPStatus
from typing import Dict, List, cast

from collector_utilities.type import JSON, URL, Response, Responses

from .source_collector import SourceCollector, SourceResponses


class FakeResponse:
    """Fake a response because aiohttp.ClientResponse can not easily be instantiated directly. """
    status = HTTPStatus.OK

    def __init__(self, contents: bytes = bytes()) -> None:
        super().__init__()
        self.contents = contents

    async def json(self, content_type=None) -> JSON:  # pylint: disable=unused-argument
        """Return the JSON version of the contents."""
        return cast(JSON, json.loads(self.contents))

    async def text(self) -> str:
        """Return the text version of the contents."""
        return str(self.contents.decode())


class FileSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve files."""

    file_extensions: List[str] = []  # Subclass responsibility

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        responses = await super()._get_source_responses(*urls)
        if urls[0].endswith(".zip"):
            unzipped_responses = await asyncio.gather(*[self.__unzip(response) for response in responses])
            responses[:] = list(itertools.chain(*unzipped_responses))
        return responses

    def _headers(self) -> Dict[str, str]:
        headers = super()._headers()
        if token := cast(str, self._parameter("private_token")):
            # GitLab needs this header, see
            # https://docs.gitlab.com/ee/api/jobs.html#download-a-single-artifact-file-by-job-id
            headers["Private-Token"] = token
        return headers

    @classmethod
    async def __unzip(cls, response: Response) -> Responses:
        """Unzip the response content and return a (new) response for each applicable file in the zip archive."""
        with zipfile.ZipFile(io.BytesIO(await response.read())) as response_zipfile:
            names = [name for name in response_zipfile.namelist() if name.split(".")[-1].lower() in cls.file_extensions]
            responses = [FakeResponse(response_zipfile.read(name)) for name in names]
        return cast(Responses, responses)


class CSVFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve CSV files."""

    file_extensions = ["csv"]


class HTMLFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve HTML files."""

    file_extensions = ["html", "htm"]


class JSONFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve JSON files."""

    file_extensions = ["json"]


class XMLFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve XML files."""

    file_extensions = ["xml"]
