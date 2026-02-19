"""Unit tests for the file system module."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from filesystem import glob, update_file, update_files


@patch("pathlib.Path.cwd", Mock(return_value=Path("/")))
@patch("pathlib.Path.glob")
class GlobTest(unittest.TestCase):
    """Unit tests for the glob function."""

    def test_one_file(self, mock_glob: Mock):
        """Test that a file is returned."""
        mock_glob.return_value = [Path("/file.txt")]
        self.assertEqual([Path("/file.txt")], list(glob("*.txt")))

    def test_multiple_files(self, mock_glob: Mock):
        """Test that multiple files are returned."""
        mock_glob.return_value = [Path("/file.txt"), Path("/folder/another_file.txt")]
        self.assertEqual([Path("/file.txt"), Path("/folder/another_file.txt")], list(glob("*.txt")))

    def test_start_folder(self, mock_glob: Mock):
        """Test that a different start folder can be passed."""
        mock_glob.return_value = [Path("/example/file.txt")]
        self.assertEqual([Path("/example/file.txt")], list(glob("*.txt", start=Path("/example"))))

    def test_ignore_folders(self, mock_glob: Mock):
        """Test that some folders are ignored."""
        folders_that_should_be_ignored = ["/project/build", "/example/node_modules", "/src/__pycache__", "/.git"]
        mock_glob.return_value = [Path(folder) / "file.txt" for folder in folders_that_should_be_ignored]
        self.assertEqual([], list(glob("*.txt")))


REGEXP = r"image: (?P<dependency>[\w\d\./-]+):(?P<version>[\d\w\.\-]+)"


class UpdateFileTest(unittest.TestCase):
    """Unit tests for the update file function."""

    def test_no_changes(self):
        """Test no changes."""
        mock_file = Mock(read_text=Mock(return_value="line1\nline2\n"))
        mock_logger = Mock()
        update_file(mock_file, "regexp", lambda *_args: "1.1", mock_logger)
        mock_file.write_text.assert_not_called()
        mock_logger.new_version.assert_not_called()

    def test_new_version(self):
        """Test a new version."""
        mock_file = Mock(read_text=Mock(return_value="line1\nimage: python:3.14\n"))
        mock_logger = Mock()
        update_file(mock_file, REGEXP, lambda *_args: "3.15", mock_logger)
        mock_file.write_text.assert_called_with("line1\nimage: python:3.15\n")
        mock_logger.new_version.assert_called_with("python", "3.15")

    def test_old_version(self):
        """Test a new version that is actually older."""
        mock_file = Mock(read_text=Mock(return_value="line1\nimage: python:3.14\n"))
        mock_logger = Mock()
        update_file(mock_file, REGEXP, lambda *_args: "3.13", mock_logger)
        mock_file.write_text.assert_not_called()
        mock_logger.new_version.assert_not_called()


@patch("pathlib.Path.glob")
class UpdateFilesTest(unittest.TestCase):
    """Unit tests for the update file function."""

    def mock_file(self, contents: str) -> Mock:
        """Create a mock file (Path) fixture."""
        mock_file = Mock()
        mock_file.read_text.return_value = contents
        mock_file.relative_to.return_value = Mock(parts=[])
        return mock_file

    def test_no_changes(self, mock_glob: Mock):
        """Test that files are unchanged if there is no new version."""
        mock_file = self.mock_file("line1\nline2\n")
        mock_glob.return_value = [mock_file]
        mock_logger = Mock()
        update_files("Dockerfile", REGEXP, lambda *_args: "1.1", mock_logger)
        mock_file.write_text.assert_not_called()
        mock_logger.new_version.assert_not_called()

    def test_new_version(self, mock_glob: Mock):
        """Test that files are updated with the new version."""
        mock_file = self.mock_file("line1\nimage: python:3.14\n")
        mock_glob.return_value = [mock_file]
        mock_logger = Mock()
        update_files("config.yml", REGEXP, lambda *_args: "3.15", mock_logger)
        mock_file.write_text.assert_called_with("line1\nimage: python:3.15\n")
        mock_logger.new_version.assert_called_with("python", "3.15")
