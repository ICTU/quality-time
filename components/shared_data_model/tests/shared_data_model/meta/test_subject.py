"""Unit tests for the subject meta model."""

from shared_data_model.meta.subject import Subject, Subjects

from .base import MetaModelTestCase


class SubjectTest(MetaModelTestCase):
    """Subject unit tests."""

    MODEL = Subject

    def test_get_item(self):
        """Test that subjebts can be retrieved by key."""
        subject_kwargs = dict(name="Name", description="Description", metrics=["metric_type"])
        subjects = Subjects.parse_obj(dict(subject_type=subject_kwargs))
        self.assertEqual(Subject(**subject_kwargs), subjects["subject_type"])
