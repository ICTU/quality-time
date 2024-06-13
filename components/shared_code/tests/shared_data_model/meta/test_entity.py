"""Unit tests for the entity model."""

from shared_data_model.meta.entity import Entity

from .base import MetaModelTestCase


class EntityTest(MetaModelTestCase):
    """Entity unit tests."""

    def check_entity_validation_error(self, message: str, **model_kwargs) -> None:
        """Check the validation error when instantiation the Entity model."""
        self.check_validation_error(message, Entity, **model_kwargs)

    def test_check_name_correct(self):
        """Test that a correct name passes the check."""
        entity = Entity(name="lower case", attributes=[])
        self.assertEqual("lower case", entity.name)

    def test_check_name_incorrect(self):
        """Test that an incorrect name does not pass the check."""
        model_kwargs = {"name": "Upper case", "attributes": []}
        expected_message = "String should match pattern '^[^A-Z]+$'"
        self.check_entity_validation_error(expected_message, **model_kwargs)

    def test_measured_attribute_exists(self):
        """Test that the measured attribute is an existing attribute."""
        model_kwargs = {"name": "entity", "attributes": [], "measured_attribute": "attribute"}
        expected_message = "Measured attribute attribute is not an attribute of entity entity"
        self.check_entity_validation_error(expected_message, **model_kwargs)

    def test_measured_attribute_has_number_type(self):
        """Test that the measured attribute is an existing attribute."""
        attributes = [{"name": "Attribute", "description": "Attribute."}]
        model_kwargs = {"name": "entity", "attributes": attributes, "measured_attribute": "attribute"}
        expected_message = "Measured attribute attribute does not have a number type"
        self.check_entity_validation_error(expected_message, **model_kwargs)
