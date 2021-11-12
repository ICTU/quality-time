"""File source collector base classes."""

import asyncio
import io
import itertools
import json
import zipfile
from abc import ABC
from http import HTTPStatus
from typing import cast
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from collector_utilities.type import JSON, URL, Response, Responses
from model import SourceResponses

from .source_collector import SourceCollector


class FakeResponse:
    """Fake a response because aiohttp.ClientResponse can not easily be instantiated directly."""

    status = HTTPStatus.OK

    def __init__(self, contents: bytes = bytes(), filename: str = "") -> None:
        super().__init__()
        self.contents = contents
        self.filename = filename

    async def json(self, content_type=None) -> JSON:  # pylint: disable=unused-argument
        """Return the JSON version of the contents."""
        return cast(JSON, json.loads(self.contents))

    async def text(self) -> str:
        """Return the text version of the contents."""
        return str(self.contents.decode())


class FileSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve files."""

    file_extensions: list[str] = []  # Subclass responsibility

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Extend to unzip any zipped responses."""
        responses = await super()._get_source_responses(*urls)
        if urlparse(str(urls[0])).path.endswith(".zip"):
            unzipped_responses = await asyncio.gather(*[self.__unzip(response) for response in responses])
            responses[:] = list(itertools.chain(*unzipped_responses))
        return responses

    def _headers(self) -> dict[str, str]:
        """Extend to add a private token to the headers, if present in the parameters."""
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
            if not names:
                raise LookupError(f"Zipfile contains no files with extension {' or '.join(cls.file_extensions)}")
            responses = [FakeResponse(response_zipfile.read(name), name) for name in names]
        return cast(Responses, responses)


class CSVFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve CSV files."""

    file_extensions = ["csv"]


class HTMLFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve HTML files."""

    file_extensions = ["html", "htm"]

    @staticmethod
    async def _soup(response: Response) -> Tag:
        """Return the HTML soup."""
        return BeautifulSoup(await response.text(), "html.parser")


class JSONFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve JSON files."""

    file_extensions = ["json"]


class XMLFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve XML files."""

    file_extensions = ["xml"]
