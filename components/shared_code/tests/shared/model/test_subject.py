"""Test the subject model."""

import copy

from shared.model.metric import Metric
from shared.model.report import Report
from shared.model.subject import Subject

from tests.fixtures import METRIC_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID
from tests.shared.base import DataModelTestCase


class SubjectTest(DataModelTestCase):
    """Unit tests for the subject model."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.source_data: dict = {}
        self.metric_data = {"type": "violations", "sources": {SOURCE_ID: self.source_data}, "tags": ["tag"]}
        self.subject_data = {"metrics": {METRIC_ID: self.metric_data}}
        report_data = {
            "report_uuid": REPORT_ID,
            "title": "Report",
            "subjects": {SUBJECT_ID: self.subject_data},
        }
        self.report = Report(self.DATA_MODEL, report_data)
        self.subject = self.report.subjects[0]

    def test_equality(self):
        """Test that two subjects with the same uuid are equal."""
        self.assertEqual(
            Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report),
            Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report),
        )

    def test_type(self):
        """Test that a subject has a type."""
        subject = Subject(self.DATA_MODEL, {"type": "type"}, SUBJECT_ID, self.report)
        self.assertEqual("type", subject.type)

    def test_missing_type(self):
        """Test that a subject can have a missing type."""
        subject = Subject(self.DATA_MODEL, {}, SUBJECT_ID, self.report)
        self.assertEqual(None, subject.type)

    def test_instantiate_metrics(self):
        """Test that a subject instantiates its metrics."""
        subject = Subject(self.DATA_MODEL, {"metrics": {METRIC_ID: {}}}, SUBJECT_ID, self.report)
        metric = Metric(self.DATA_MODEL, {}, METRIC_ID)
        self.assertEqual({METRIC_ID: metric}, subject.metrics_dict)

    def test_name(self):
        """Test that a subject has a name."""
        subject = Subject(self.DATA_MODEL, {"name": "Name"}, SUBJECT_ID, self.report)
        self.assertEqual("Name", subject.name)

    def test_missing_name(self):
        """Test that a subject can have a missing name."""
        subject = Subject(self.DATA_MODEL, {"type": "software"}, SUBJECT_ID, self.report)
        self.assertEqual("Software", subject.name)

    def test_missing_composite_name(self):
        """Test that a composite subject has a name."""
        subject = Subject(self.DATA_MODEL, {"type": "software_source_code"}, SUBJECT_ID, self.report)
        self.assertEqual("Software source code", subject.name)

    def test_missing_default_name(self):
        """Test that the subject name is None if both the subject and the data model have no name for the subject.

        In the current data model all subject types have a name, but in older versions they may not have.
        """
        data_model = copy.deepcopy(self.DATA_MODEL)
        data_model["subjects"]["software"]["name"] = None
        subject = Subject(data_model, {"type": "software"}, SUBJECT_ID, self.report)
        self.assertIsNone(subject.name)

    def test_summarize(self):
        """Test that a subject can be summarized."""
        metric = Metric(self.DATA_MODEL, {"type": "violations"}, METRIC_ID)
        subject = Subject(
            self.DATA_MODEL,
            {"name": "Subject", "metrics": {METRIC_ID: metric}},
            SUBJECT_ID,
            self.report,
        )
        self.assertEqual(
            {
                "name": "Subject",
                "metrics": {
                    METRIC_ID: {
                        "latest_measurement": None,
                        "recent_measurements": [],
                        "scale": "count",
                        "sources": {},
                        "status": None,
                        "status_start": None,
                        "type": "violations",
                    },
                },
            },
            subject.summarize({}),
        )

    def test_delete_tag(self):
        """Test that a tag can be deleted from all metrics in the subject."""
        self.assertEqual([METRIC_ID], self.subject.delete_tag("tag"))
        for metric in self.subject.metrics:
            self.assertNotIn("tag", metric["tags"])

    def test_delete_tag_not_found(self):
        """Test that deleting a tag that is not in the subject does not change the tags."""
        tags = {metric.uuid: metric.get("tags", []) for metric in self.subject.metrics}
        self.assertEqual([], self.subject.delete_tag("non-existing tag"))
        self.assertEqual(tags, {metric.uuid: metric.get("tags", []) for metric in self.subject.metrics})

    def test_rename_tag(self):
        """Test that a tag can be renamed for all metrics in the subject."""
        tags = {metric.uuid: metric.get("tags", []) for metric in self.subject.metrics}
        expected_tags = {uuid: ["new tag" if tag == "tag" else tag for tag in tags] for (uuid, tags) in tags.items()}
        self.assertEqual([METRIC_ID], self.subject.rename_tag("tag", "new tag"))
        self.assertEqual(expected_tags, {metric.uuid: metric.get("tags", []) for metric in self.subject.metrics})

    def test_rename_tag_not_found(self):
        """Test that renaming a tag that is not in the subject does not change the tags."""
        expected_tags = {metric.uuid: metric.get("tags", []) for metric in self.subject.metrics}
        self.assertEqual([], self.subject.rename_tag("non-existing tag", "new tag"))
        self.assertEqual(expected_tags, {metric.uuid: metric.get("tags", []) for metric in self.subject.metrics})
