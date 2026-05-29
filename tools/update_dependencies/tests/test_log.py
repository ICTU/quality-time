"""Logger unit tests."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import ANY, Mock, patch

import filesystem
from log import Logger
from version import DependencyVersion


class LoggerTests(TestCase):
    """Unit tests for the logger class."""

    @patch("logging.Logger.warning")
    def test_suppress_repeated_changelog(self, mock_warning: Mock):
        """Test that a repeated changelog is suppressed."""
        logger = Logger("suppress changelog")
        logger.new_version("dependency", DependencyVersion("1.0", "Changelog"))
        mock_warning.assert_called_once_with(
            "New version available for %s: %s\n%s", "dependency", "1.0", "Changelog", stacklevel=ANY
        )
        logger.new_version("dependency", DependencyVersion("1.0", "Changelog"))
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s",
            "dependency",
            "1.0",
            "Suppressing changelog already shown, see above",
            stacklevel=ANY,
        )


class LogOriginTests(TestCase):
    """Tests that log records are attributed to the originating updater, not the logging or filesystem helpers."""

    def test_direct_call_is_attributed_to_the_caller(self):
        """Test that a log method called directly reports the calling line as its origin."""
        logger = Logger("origin direct")
        with self.assertLogs(logger.log, level="INFO") as captured:
            logger.path(Path.cwd())
        self.assertEqual("test_log.py", Path(captured.records[0].pathname).name)

    def test_filesystem_helper_call_is_attributed_to_the_caller(self):
        """Test that logs emitted via the filesystem helper report the helper's caller, not filesystem.py, as origin."""
        logger = Logger("origin helper")
        with TemporaryDirectory() as directory:
            (Path(directory) / "config.yml").write_text("dependency: 1.0\n")
            with (
                patch("pathlib.Path.cwd", Mock(return_value=Path(directory))),
                self.assertLogs(logger.log, level="INFO") as captured,
            ):
                filesystem.update_files(
                    "*.yml",
                    r"(?P<dependency>dependency): (?P<version>[\d.]+)",
                    lambda *_args: DependencyVersion("2.0"),
                    logger,
                    start=Path(directory),
                )
        origins = {Path(record.pathname).name for record in captured.records}
        self.assertEqual({"test_log.py"}, origins)
