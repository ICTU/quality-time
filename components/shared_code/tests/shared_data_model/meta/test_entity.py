"""Unit tests for the entity model."""

from shared_data_model.meta.entity import Entity

from .base import MetaModelTestCase


class EntityTest(MetaModelTestCase):
    """Entity unit tests."""

    MODEL = Entity

    def test_check_name_correct(self):
        """Test that a correct name passes the check."""
        entity = Entity(name="lower case", attributes=[])
        self.assertEqual("lower case", entity.name)

    def test_check_name_incorrect(self):
        """Test that an incorrect name does not pass the check."""
        self.check_validation_error("String should match pattern '^[^A-Z]+$'", name="Upper case", attributes=[])

    def test_measured_attribute_exists(self):
        """Test that the measured attribute is an existing attribute."""
        self.check_validation_error(
            "Measured attribute attribute is not an attribute of entity entity",
            name="entity",
            attributes=[],
            measured_attribute="attribute",
        )

    def test_measured_attribute_has_number_type(self):
        """Test that the measured attribute is an existing attribute."""
        self.check_validation_error(
            "Measured attribute attribute does not have a number type",
            name="entity",
            attributes=[{"name": "Attribute", "description": "Attribute."}],
            measured_attribute="attribute",
        )
