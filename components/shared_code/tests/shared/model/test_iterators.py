"""Unit tests for the model iterators."""

import unittest

from shared.model.iterators import issue_trackers, metrics, sources, subjects


class SubjectIteratorTest(unittest.TestCase):
    """Unit test for the subject iterator."""

    def test_empty_report(self):
        """Test that an empty report contains no subjects."""
        self.assertEqual([], list(subjects({})))

    def test_one_subject(self):
        """Test that the subject is returned."""
        self.assertEqual([{}], list(subjects({"subjects": {"subject_uuid": {}}})))


class MetricIteratorTest(unittest.TestCase):
    """Unit test for the metric iterator."""

    def test_empty_report(self):
        """Test that an empty report contains no metrics."""
        self.assertEqual([], list(metrics({})))

    def test_one_metric(self):
        """Test that the metric is returned."""
        self.assertEqual([{}], list(metrics({"subjects": {"subject_uuid": {"metrics": {"metric_uuid": {}}}}})))


class SourceIteratorTest(unittest.TestCase):
    """Unit test for the source iterator."""

    def test_empty_report(self):
        """Test that an empty report contains no sources."""
        self.assertEqual([], list(sources({})))

    def test_one_source(self):
        """Test that the source is returned."""
        self.assertEqual(
            [{}],
            list(
                sources({"subjects": {"subject_uuid": {"metrics": {"metric_uuid": {"sources": {"source_uuid": {}}}}}}})
            ),
        )


class IssueTrackerIteratorTest(unittest.TestCase):
    """Unit test for the issue tracker iterator."""

    def test_empty_report(self):
        """Test that an empty report contains no issue tracker."""
        self.assertEqual([], list(issue_trackers({})))

    def test_one_issue_tracker(self):
        """Test that the issue tracker is returned."""
        self.assertEqual([{"type": "jira"}], list(issue_trackers({"issue_tracker": {"type": "jira"}})))
