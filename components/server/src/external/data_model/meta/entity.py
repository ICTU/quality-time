"""Data model measurement entities."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator  # pylint: disable=no-name-in-module

from .base import NamedModel


class Color(str, Enum):
    """Entity color, corresponding to the Semantic UI React states for table rows.

    See https://react.semantic-ui.com/collections/table/#states-positive-negative.
    """

    ACTIVE = "active"
    ERROR = "error"
    NEGATIVE = "negative"
    POSITIVE = "positive"
    WARNING = "warning"


class EntityAttributeType(str, Enum):
    """Type of the entity attribute. If not specified, the entity attribute type is string."""

    DATE = "date"
    DATETIME = "datetime"
    FLOAT = "float"
    MINUTES = "minutes"
    INTEGER = "integer"
    STATUS = "status"


class EntityAttribute(NamedModel):  # pylint: disable=too-few-public-methods
    """Attributes of measurement entities."""

    key: Optional[str] = None
    help: Optional[str] = None
    url: Optional[str] = None  # Which key to use to get the URL for this attribute
    color: Optional[dict[str, Color]] = None
    type: Optional[EntityAttributeType] = None
    pre: Optional[bool] = None  # Should the attribute be formatted using <pre></pre>? Defaults to False
    visible: Optional[bool] = None  # Should this attribute be visible in the UI? Defaults to True

    @validator("key", always=True)
    def set_key(cls, key, values):  # pylint: disable=no-self-argument,no-self-use
        """Set the key to the lower case version of the name if there's no key."""
        return values["name"].lower().replace(" ", "_") if not key else key


class Entity(BaseModel):  # pylint: disable=too-few-public-methods
    """Measurement entity (violation, warning, etc.)."""

    # Entity is not derived from NamedModel because entity names should be lower case

    name: str = Field(..., regex=r"[a-z]+")
    name_plural: Optional[str] = None
    attributes: list[EntityAttribute]
    measured_attribute: Optional[str] = None

    @validator("name_plural", always=True)
    def set_name_plural(cls, name_plural, values):  # pylint: disable=no-self-argument,no-self-use
        """Set the plural name if no value was supplied."""
        return values.get("name", "") + "s" if not name_plural else name_plural

    @validator("measured_attribute")
    def check_measured_attribute(cls, measured_attribute, values):  # pylint: disable=no-self-argument,no-self-use
        """Check that the measured attribute is a valid attribute with a number type."""
        attributes = {attribute.key: attribute.type for attribute in values.get("attributes", [])}
        if measured_attribute and measured_attribute not in attributes:
            raise ValueError(
                f"Measured attribute {measured_attribute} is not an attribute of entity {values.get('name')}"
            )
        if attributes[measured_attribute] not in (
            EntityAttributeType.FLOAT,
            EntityAttributeType.INTEGER,
            EntityAttributeType.MINUTES,
        ):
            raise ValueError(f"Measured attribute {measured_attribute} does not have a number type")
        return measured_attribute


class Entities(BaseModel):  # pylint: disable=too-few-public-methods
    """Entity mapping."""

    __root__: dict[str, Entity]
