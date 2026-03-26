"""Unit tests for file source collectors."""

import io
import unittest
from unittest.mock import Mock
from zipfile import ZipFile

import aiohttp

from base_collectors.file_source_collector import FileSourceCollector
from collector_utilities.type import URL


class FileSourceCollectorTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the file source collector."""

    async def test_is_zip_when_path_ends_with_zip(self):
        """Test that a response with a zip file is detected by path."""
        response = Mock(spec=aiohttp.ClientResponse)
        self.assertTrue(await FileSourceCollector.is_zipped(URL("https://url/download.zip"), response))

    async def test_is_zip_when_content_type_is_zip(self):
        """Test that a response with a zip file is detected by content type."""
        response = Mock(spec=aiohttp.ClientResponse)
        response.content_type = "application/zip"
        self.assertTrue(await FileSourceCollector.is_zipped(URL("https://url/download"), response))

    async def test_is_zip_when_zip_in_content_disposition(self):
        """Test that a response with a zip file is detected by content disposition."""
        response = Mock(spec=aiohttp.ClientResponse)
        response.content_disposition = 'attachment; filename="filename.zip"'
        self.assertTrue(await FileSourceCollector.is_zipped(URL("https://url/download"), response))

    async def test_is_zip_when_checked_by_magic_number(self):
        """Test that a response with a zip file is detected by magic number."""
        response = Mock(spec=aiohttp.ClientResponse)
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zipfile:
            zipfile.writestr("dummy.txt", "Dummy data")
        response.read.return_value = zip_buffer.getvalue()
        self.assertTrue(await FileSourceCollector.is_zipped(URL("https://url/download"), response))

    async def test_is_not_zip_when_random_bytes(self):
        """Test that a response with random bytes is not detected as zip."""
        response = Mock(spec=aiohttp.ClientResponse)
        zip_buffer = io.BytesIO(b"Dummy data")
        response.read.return_value = zip_buffer.getvalue()
        self.assertFalse(await FileSourceCollector.is_zipped(URL("https://url/download"), response))

    async def test_is_not_zip_when_no_contents(self):
        """Test that a response without contents is not detected as zip."""
        response = Mock(spec=aiohttp.ClientResponse)
        zip_buffer = io.BytesIO(b"")
        response.read.return_value = zip_buffer.getvalue()
        self.assertFalse(await FileSourceCollector.is_zipped(URL("https://url/download"), response))
