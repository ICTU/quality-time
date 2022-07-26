"""Unit tests for the base models."""

from shared_data_model.meta.base import DescribedModel, MappedModel

from .base import MetaModelTestCase


class DescribedModelTest(MetaModelTestCase):
    """Unit tests for described models."""

    MODEL = DescribedModel

    def test_description(self):
        """Test that a correct description passes the check and that a dot is added."""
        self.assertEqual(
            "Description.", DescribedModel.parse_obj(dict(name="Name", description="Description")).description
        )

    def test_description_with_punctuation(self):
        """Test that a description with punctuation passes the check."""
        self.assertEqual(
            "Description?", DescribedModel.parse_obj(dict(name="Name", description="Description?")).description
        )

    def test_missing_description(self):
        """Test that the description is mandatory."""
        self.check_validation_error("description\n  field required", name="Name")

    def test_empty_description(self):
        """Test that the description has a non-zero length."""
        self.check_validation_error('description\n  string does not match regex ".+"', name="Name", description="")


class MappedModelTest(MetaModelTestCase):
    """Unit tests for mapped models."""

    def setUp(self):
        """Extend to setup the model."""
        super().setUp()
        described_model_kwargs = dict(name="Name", description="Description")
        self.mapped_model = MappedModel[DescribedModel].parse_obj(dict(described_model_type=described_model_kwargs))
        self.expected_described_model = DescribedModel(**described_model_kwargs)

    def test_get_item(self):
        """Test that values can be retrieved by key."""
        self.assertEqual(self.expected_described_model, self.mapped_model["described_model_type"])

    def test_items(self):
        """Test that the items can be retrieved."""
        self.assertEqual([("described_model_type", self.expected_described_model)], list(self.mapped_model.items()))
