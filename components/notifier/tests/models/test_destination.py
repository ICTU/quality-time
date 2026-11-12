"""Unit tests for the notification destination."""

import unittest

from models.destination import Destination


class DestinationTest(unittest.TestCase):
    """Unit tests for the notification destination."""

    def test_from_dict(self):
        """Test that the trailing slash is removed from the report URL."""
        destination = Destination.from_dict({"webhook": "https://webhook", "report_url": "https://r/"})
        self.assertEqual(Destination("https://webhook", "https://r"), destination)

    def test_from_dict_without_report_url(self):
        """Test that the report URL is empty if the destination has no report URL."""
        destination = Destination.from_dict({"webhook": "https://webhook"})
        self.assertEqual("", destination.report_url)
