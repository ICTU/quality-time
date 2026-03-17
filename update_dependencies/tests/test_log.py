"""Logger unit tests."""

from unittest import TestCase
from unittest.mock import Mock, patch

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
            "New version available for %s: %s\n%s", "dependency", "1.0", "Changelog", stacklevel=2
        )
        logger.new_version("dependency", DependencyVersion("1.0", "Changelog"))
        mock_warning.assert_called_with(
            "New version available for %s: %s\n%s",
            "dependency",
            "1.0",
            "Suppressing changelog already shown, see above",
            stacklevel=2,
        )
