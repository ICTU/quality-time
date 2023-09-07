"""Data model measurement entities."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import NamedModel, StrEnum


class Color(StrEnum):
    """Entity color, corresponding to the Semantic UI React states for table rows.

    See https://react.semantic-ui.com/collections/table/#states-positive-negative.
    """

    ACTIVE = "active"
    ERROR = "error"
    NEGATIVE = "negative"
    POSITIVE = "positive"
    WARNING = "warning"


class EntityAttributeType(StrEnum):
    """Type of the entity attribute. If not specified, the entity attribute type is string."""

    DATE = "date"
    DATETIME = "datetime"
    FLOAT = "float"
    INTEGER = "integer"
    STATUS = "status"


class EntityAttributeAligment(StrEnum):
    """Alignment of the entity attribute."""

    LEFT = "left"
    RIGHT = "right"


class EntityAttribute(NamedModel):
    """Attributes of measurement entities."""

    # Use the value property of enums, needed so model.dict() gets the value of enums:
    model_config = ConfigDict(use_enum_values=True)

    key: str | None = None
    help: str | None = None  # noqa: A003
    url: str | None = None  # Which key to use to get the URL for this attribute
    color: dict[str, Color] | None = None
    type: EntityAttributeType | None = None  # noqa: A003
    alignment: EntityAttributeAligment | None = None  # If not given, the aligment is based on the attribute type
    pre: bool | None = None  # Should the attribute be formatted using <pre></pre>? Defaults to False
    visible: bool | None = None  # Should this attribute be visible in the UI? Defaults to True

    @model_validator(mode="after")
    def set_key(self) -> Self:
        """Set the key to the lower case version of the name if there's no key."""
        if self.key is None:
            self.key = self.name.lower().replace(" ", "_")
        return self


class Entity(BaseModel):
    """Measurement entity (violation, warning, etc.)."""

    # Entity is not derived from NamedModel because entity names should be lower case

    name: str = Field(..., pattern=r"^[^A-Z]+$")
    name_plural: str | None = None
    attributes: list[EntityAttribute]
    measured_attribute: str | None = None

    @model_validator(mode="after")
    def set_name_plural(self) -> Self:
        """Set the plural name if no value was supplied."""
        if self.name_plural is None:
            self.name_plural = self.name + "s"
        return self

    @model_validator(mode="after")
    def check_measured_attribute(self) -> Self:
        """Check that the measured attribute is a valid attribute with a number type."""
        if self.measured_attribute:
            attributes = {attribute.key: attribute.type for attribute in self.attributes}
            if self.measured_attribute not in attributes:
                msg = f"Measured attribute {self.measured_attribute} is not an attribute of entity {self.name}"
                raise ValueError(msg)
            if attributes[self.measured_attribute] not in (EntityAttributeType.FLOAT, EntityAttributeType.INTEGER):
                msg = f"Measured attribute {self.measured_attribute} does not have a number type"
                raise ValueError(msg)
        return self
