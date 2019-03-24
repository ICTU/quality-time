"""Unit tests for the measurement routes."""

import unittest
from unittest.mock import Mock, patch

from src.routes.measurement import post_measurement


class PostMeasurementTests(unittest.TestCase):
    """Unit tests for the post measurement route."""

    def test_first_measurement(self):
        """Post the first measurement for a metric."""
        database = Mock()
        database.measurements.find_one = Mock(return_value=None)
        def set_measurement_id(measurement):
            measurement["_id"] = "measurement_id"
        database.measurements.insert_one = Mock(side_effect=set_measurement_id)
        database.reports.distinct = Mock(return_value=["report_uuid"])
        database.reports.find_one = Mock(
            return_value=dict(
                _id="report_uuid",
                subjects=dict(
                    s=dict(
                        metrics=dict(
                            metric_uuid=dict(
                                type="metric_type", target="0", debt_target=None, accept_debt=False, tags=[]))))))
        database.datamodels.find_one = Mock(return_value=dict(_id="", metrics=dict(metric_type=dict(direction="<="))))
        with patch("bottle.request") as request:
            request.json = dict(metric_uuid="metric_uuid", sources=[])
            post_measurement(database)
        database.measurements.insert_one.assert_called_once()

    def test_unchanged_measurement(self):
        """Post an unchanged measurement for a metric."""
        database = Mock()
        database.measurements.find_one = Mock(return_value=dict(_id="id", sources=[]))
        database.measurements.update_one = Mock()
        with patch("bottle.request") as request:
            request.json = dict(metric_uuid="metric_uuid", sources=[])
            post_measurement(database)
        database.measurements.update_one.assert_called_once()
