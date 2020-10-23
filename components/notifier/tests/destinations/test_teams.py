"""Unit tests for the Teams notification destination."""

import logging
import json
import pathlib
from unittest import mock, TestCase

from destinations.ms_teams import build_notification_text, send_notification_to_teams, get_status


@mock.patch('pymsteams.connectorcard.send')
class SendNotificationToTeamsTests(TestCase):
    """Unit tests for the Teams destination for notifications."""

    def setUp(self):
        """Provide the text contents to the rest of the class."""
        self.message = "notification message"

    def test_invalid_webhook(self, mock_send):
        """Test that exceptions are caught."""
        logging.disable(logging.CRITICAL)  # Don't log to stderr during this unit test
        mock_send.side_effect = OSError("Some error")
        send_notification_to_teams("invalid_webhook", self.message)
        mock_send.assert_called()
        logging.disable(logging.NOTSET)  # Reset the logging

    def test_valid_webhook(self, mock_send):
        """Test that a valid message is sent to a valid webhook."""
        send_notification_to_teams("valid_webhook", self.message)
        mock_send.assert_called()


class BuildNotificationTextTests(TestCase):
    """Unit tests for the message builder."""

    @classmethod
    def setUpClass(cls) -> None:
        """Provide the data_model to the rest of the class."""
        module_dir = pathlib.Path(__file__).resolve().parent
        data_model_path = module_dir.parent.parent.parent / "server" / "src" / "data" / "datamodel.json"
        with data_model_path.open() as json_data_model:
            cls.data_model = json.load(json_data_model)


    def test_text(self):
        """Test that the text is correct."""
        api_values = {"target met (green)": "target_met",
                        "near target met (yellow)": "near_target_met",
                        "target not met (red)": "target_not_met",
                        "technical debt target met (grey)": "debt_target_met",
                        "unknown (white)": "unknown"}
        status = {"api_values": api_values}
        parameters = {"status": status}
        quality_time = {"parameters": parameters}
        sources = {"quality_time": quality_time}

        name = "Test metric"
        unit = "bad"
        metric_type = {"name": name, "unit": unit}
        metrics = {"metric_type": metric_type}

        data_model = {"sources": sources, "metrics": metrics}

        text = build_notification_text(
            dict(
                report_uuid="report1", report_title="Report 1",
                new_red_metrics=2, url="http://report1", teams_webhook="",
                metrics=[dict(
                        metric_type="metric_type",
                        metric_name="name",
                        metric_unit="unit",
                        old_metric_status="near_target_met",
                        old_metric_value=5,
                        new_metric_status="target_not_met",
                        new_metric_value=10),
                    dict(
                        metric_type="metric_type",
                        metric_name="name",
                        metric_unit="unit",
                        old_metric_status="target_met",
                        old_metric_value=5,
                        new_metric_status="target_not_met",
                        new_metric_value=10)]), data_model)
        contents = text.split(", ", 1)
        self.assertEqual("[Report 1](http://report1) has 2 metrics that turned red.<br> "
                         "Test metric status is target not met (red), "
                         "was near target met (yellow). Value is 10bad was 5bad.<br> "
                         "Test metric status is target not met (red), "
                         "was target met (green). Value is 10bad was 5bad.",
                         contents[1])


    def test_unknown_status(self):
        """"Test that the return value is correct."""
        self.assertEqual("Unknown status", get_status("", self.data_model))
