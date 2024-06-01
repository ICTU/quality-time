"""Unit tests for the subject model."""

from shared_data_model.meta.subject import Subject

from .base import MetaModelTestCase


class SubjectTest(MetaModelTestCase):
    """Unit tests for the subject model."""

    MODEL = Subject

    def test_all_metrics(self):
        """Test that the all_metrics property of a subject returns all metrics recursively and deduplicated."""
        subject = Subject(
            name="Subject",
            description="Description.",
            metrics=["parent metric"],
            subjects={
                "child_subject1": Subject(
                    name="Child subject 1", description="Child 1 description.", metrics=["child metric"]
                ),
                "child_subject2": Subject(
                    name="Child subject 2", description="Child 2 description.", metrics=["child metric"]
                ),
            },
        )
        self.assertEqual(["child metric", "parent metric"], subject.all_metrics)
