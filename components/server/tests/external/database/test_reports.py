"""Test the reports collection."""

import unittest
from unittest.mock import Mock

from external.database.reports import metrics_of_subject

from ...fixtures import METRIC_ID, METRIC_ID2, SUBJECT_ID


class MetricsForSubjectTest(unittest.TestCase):
    """Unittest for getting all metrics belonging to a single subject."""

    def setUp(self):
        """Override to create a mock database fixture."""
        self.database = Mock()
        self.database.reports.find_one.return_value = {
            "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {}, METRIC_ID2: {}}}}
        }

    def test_metrics_of_subject(self):
        """Test if we get all metric id's in the subject."""
        metric_uuids = metrics_of_subject(self.database, SUBJECT_ID)

        self.assertEqual(len(metric_uuids), 2)
        for m_id in metric_uuids:
            self.assertIn(m_id, [METRIC_ID, METRIC_ID2])
