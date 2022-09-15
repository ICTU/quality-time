"""Unit tests for the migration code."""

import unittest
from unittest.mock import call, Mock

from bson.objectid import ObjectId
from pymongo.operations import UpdateOne, DeleteMany

from initialization.migration import merge_unmerged_measurements

from ..fixtures import METRIC_ID, METRIC_ID2


class MergeUnmergedMeasurementsMigrationTest(unittest.TestCase):
    """Unit tests for the 'merge unmerged measurements' migration."""

    def setUp(self) -> None:
        """Override to set up database fixture."""
        self.database = Mock()
        self.database.measurements.estimated_document_count.return_value = 42  # Only used for logging

    def test_no_metrics(self):
        """Test that no measurements are merged if there are no metrics."""
        self.database.measurements.distinct.return_value = []
        self.database.measurements.find.return_value = []
        merge_unmerged_measurements(self.database)
        self.database.bulk_write.assert_not_called()

    def test_one_measurement(self):
        """Test that no measurements are merged if there is just one measurement."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-01"},
        ]
        merge_unmerged_measurements(self.database)
        self.database.bulk_write.assert_not_called()

    def test_two_different_measurements(self):
        """Test that no measurements are merged if there are two different measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": ObjectId(), "count": dict(value="2"), "end": "2020-01-02"},
        ]
        merge_unmerged_measurements(self.database)
        self.database.bulk_write.assert_not_called()

    def test_two_equal_measurements(self):
        """Test that measurements are merged if there are two equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
        ]
        merge_unmerged_measurements(self.database)
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-02")}),
                DeleteMany({"_id": {"$in": [object_id2]}}),
            ]
        )

    def test_three_equal_measurements(self):
        """Test that measurements are merged if there are three equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
            {"_id": (object_id3 := ObjectId()), "count": dict(value="1"), "end": "2020-01-03"},
        ]
        merge_unmerged_measurements(self.database)
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-03")}),
                DeleteMany({"_id": {"$in": [object_id2, object_id3]}}),
            ]
        )

    def test_two_times_two_equal_measurements(self):
        """Test that measurements are merged if there are two times two equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
            {"_id": (object_id3 := ObjectId()), "count": dict(value="2"), "end": "2020-01-03"},
            {"_id": (object_id4 := ObjectId()), "count": dict(value="2"), "end": "2020-01-04"},
        ]
        merge_unmerged_measurements(self.database)
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-02")}),
                UpdateOne({"_id": object_id3}, {"$set": dict(end="2020-01-04")}),
                DeleteMany({"_id": {"$in": [object_id2, object_id4]}}),
            ]
        )

    def test_two_metrics_with_two_equal_measurements_each(self):
        """Test that measurements are merged for multiple metrics if they have two equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID, METRIC_ID2]
        self.database.measurements.find.side_effect = [
            [
                {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
                {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
            ],
            [
                {"_id": (object_id3 := ObjectId()), "count": dict(value="2"), "end": "2020-01-03"},
                {"_id": (object_id4 := ObjectId()), "count": dict(value="2"), "end": "2020-01-04"},
            ],
        ]
        merge_unmerged_measurements(self.database)
        self.database.measurements.bulk_write.assert_has_calls(
            [
                call(
                    [
                        UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-02")}),
                        DeleteMany({"_id": {"$in": [object_id2]}}),
                    ]
                ),
                call(
                    [
                        UpdateOne({"_id": object_id3}, {"$set": dict(end="2020-01-04")}),
                        DeleteMany({"_id": {"$in": [object_id4]}}),
                    ]
                ),
            ]
        )
