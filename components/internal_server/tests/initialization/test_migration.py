"""Unit tests for the migration code."""

import unittest
from unittest.mock import call, Mock

from bson.objectid import ObjectId
from pymongo.operations import UpdateOne, DeleteMany

from shared.model.report import Report
from initialization.migration import merge_unmerged_measurements, rename_issue_lead_time, Stats

from ..base import DataModelTestCase
from ..fixtures import METRIC_ID, METRIC_ID2, SUBJECT_ID, create_report


class MergeUnmergedMeasurementsMigrationTest(unittest.TestCase):
    """Unit tests for the 'merge unmerged measurements' migration."""

    def setUp(self) -> None:
        """Override to set up database fixture."""
        self.database = Mock()
        self.database.measurements.estimated_document_count.return_value = 42  # Only used for logging

    def merge(self, dry_run: bool = False) -> Stats:
        """Merge the measurements."""
        return merge_unmerged_measurements(self.database, dry_run=dry_run)

    def check_backups(self, *backups: tuple[list[ObjectId], list[ObjectId]]) -> None:
        """Check that the correct measurements were backed up."""
        if backups:
            calls = []
            for backup in backups:
                for object_ids, operation in zip(backup, ("updated", "deleted")):
                    destination_collection = f"backup_{operation}_measurements"
                    calls.append(
                        call(
                            [
                                {"$match": {"_id": {"$in": object_ids}}},
                                {"$merge": {"into": destination_collection, "on": "_id", "whenMatched": "replace"}},
                            ]
                        )
                    )
            self.database.measurements.aggregate.assert_has_calls(calls)
        else:
            self.database.measurements.aggregate.assert_not_called()

    def test_no_metrics(self):
        """Test that no measurements are merged if there are no metrics."""
        self.database.measurements.distinct.return_value = []
        self.database.measurements.find.return_value = []
        self.assertEqual(Stats(0, 0, 0, 0), self.merge())
        self.database.bulk_write.assert_not_called()
        self.check_backups()

    def test_one_measurement(self):
        """Test that no measurements are merged if there is just one measurement."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-01"},
        ]
        self.assertEqual(Stats(0, 0, 1, 1), self.merge())
        self.database.bulk_write.assert_not_called()
        self.check_backups()

    def test_two_measurements_with_same_scale_different_values(self):
        """Test that no measurements are merged if there are two different measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": ObjectId(), "count": dict(value="2"), "end": "2020-01-02"},
        ]
        self.assertEqual(Stats(0, 0, 2, 1), self.merge())
        self.database.bulk_write.assert_not_called()
        self.check_backups()

    def test_two_measurements_with_differtent_scale_same_values(self):
        """Test that no measurements are merged if there are two different measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": ObjectId(), "percentage": dict(value="1"), "end": "2020-01-02"},
        ]
        self.assertEqual(Stats(0, 0, 2, 1), self.merge())
        self.database.bulk_write.assert_not_called()
        self.check_backups()

    def test_two_equal_measurements(self):
        """Test that measurements are merged if there are two equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
        ]
        self.assertEqual(Stats(1, 1, 2, 1), self.merge())
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-02")}),
                DeleteMany({"_id": {"$in": [object_id2]}}),
            ]
        )
        self.check_backups(([object_id1], [object_id2]))

    def test_two_equal_measurements_where_later_one_ends_earlier(self):
        """Test that measurements are merged if there are two equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
        ]
        self.assertEqual(Stats(1, 1, 2, 1), self.merge())
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-02")}),
                DeleteMany({"_id": {"$in": [object_id2]}}),
            ]
        )
        self.check_backups(([object_id1], [object_id2]))

    def test_three_equal_measurements(self):
        """Test that measurements are merged if there are three equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
            {"_id": (object_id3 := ObjectId()), "count": dict(value="1"), "end": "2020-01-03"},
        ]
        self.assertEqual(Stats(1, 2, 3, 1), self.merge())
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-03")}),
                DeleteMany({"_id": {"$in": [object_id2, object_id3]}}),
            ]
        )
        self.check_backups(([object_id1], [object_id2, object_id3]))

    def test_two_times_two_equal_measurements(self):
        """Test that measurements are merged if there are two times two equal measurements."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": (object_id1 := ObjectId()), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": (object_id2 := ObjectId()), "count": dict(value="1"), "end": "2020-01-02"},
            {"_id": (object_id3 := ObjectId()), "count": dict(value="2"), "end": "2020-01-03"},
            {"_id": (object_id4 := ObjectId()), "count": dict(value="2"), "end": "2020-01-04"},
        ]
        self.assertEqual(Stats(2, 2, 4, 1), self.merge())
        self.database.measurements.bulk_write.assert_called_once_with(
            [
                UpdateOne({"_id": object_id1}, {"$set": dict(end="2020-01-02")}),
                UpdateOne({"_id": object_id3}, {"$set": dict(end="2020-01-04")}),
                DeleteMany({"_id": {"$in": [object_id2, object_id4]}}),
            ]
        )
        self.check_backups(([object_id1, object_id3], [object_id2, object_id4]))

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
        self.assertEqual(Stats(2, 2, 4, 2), self.merge())
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
        self.check_backups(([object_id1], [object_id2]), ([object_id3], [object_id4]))

    def test_two_equal_measurements_with_dry_run(self):
        """Test that measurements are not merged if there are two equal measurements but we're dry running."""
        self.database.measurements.distinct.return_value = [METRIC_ID]
        self.database.measurements.find.return_value = [
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-01"},
            {"_id": ObjectId(), "count": dict(value="1"), "end": "2020-01-02"},
        ]
        self.assertEqual(Stats(1, 1, 2, 1), self.merge(dry_run=True))
        self.database.bulk_write.assert_not_called()
        self.check_backups()


class RenameIssueLeadTimeMigrationTest(DataModelTestCase):
    """Unit tests for the 'rename issue lead time' migration."""

    def setUp(self) -> None:
        """Override to set up database fixture."""
        self.database = Mock()

    def rename(self) -> None:
        """Rename the metrics."""
        return rename_issue_lead_time(self.database)

    def test_rename(self):
        """Test that the renaming of metrics works."""
        test_report = create_report()
        report_id = ObjectId()

        test_report["_id"] = report_id
        test_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["type"] = "lead_time_for_changes"
        self.database.reports.find.return_value = [Report(self.DATA_MODEL, test_report)]
        self.rename()

        self.database.reports.replace_one.assert_called_once()
        mock_call_args = self.database.reports.replace_one.call_args.args
        self.assertIn({"_id": report_id}, mock_call_args)
        self.assertEqual(
            "average_issue_lead_time", mock_call_args[1]["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["type"]
        )

    def test_no_change(self):
        """Test that the migration does not touch other metrics."""
        self.database.reports.find.return_value = [Report(self.DATA_MODEL, create_report())]
        self.rename()
        self.database.reports.replace_one.assert_not_called()
