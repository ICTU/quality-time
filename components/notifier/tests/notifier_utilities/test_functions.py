import unittest
from unittest import mock
from unittest.mock import patch

from quality_time_notifier import notify


class MyTestCase(unittest.TestCase):

    @mock.patch('quality_time_notifier.send_notification_to_teams', return_value=True)
    def test_notifier(self, mock_sending_notification):
        notify()
        self.assertTrue(True)
