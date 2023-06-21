"""Data model measurement entities."""

from pydantic import BaseModel, Field, validator

from .base import MappedModel, NamedModel, StrEnum


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

    key: str | None = None
    help: str | None = None  # noqa: A003
    url: str | None = None  # Which key to use to get the URL for this attribute
    color: dict[str, Color] | None = None
    type: EntityAttributeType | None = None  # noqa: A003
    alignment: EntityAttributeAligment | None = None  # If not given, the aligment is based on the attribute type
    pre: bool | None = None  # Should the attribute be formatted using <pre></pre>? Defaults to False
    visible: bool | None = None  # Should this attribute be visible in the UI? Defaults to True

    @validator("key", always=True)
    def set_key(cls, key: str, values: dict[str, str]) -> str:
        """Set the key to the lower case version of the name if there's no key."""
        return key if key else values["name"].lower().replace(" ", "_")

    class Config:
        """Pydantic configuration for this model class."""

        use_enum_values = True  # Use the value property of enums, needed so model.dict() gets the value of enums


class Entity(BaseModel):
    """Measurement entity (violation, warning, etc.)."""

    # Entity is not derived from NamedModel because entity names should be lower case

    name: str = Field(..., regex=r"[a-z]+")
    name_plural: str | None = None
    attributes: list[EntityAttribute]
    measured_attribute: str | None = None

    @validator("name_plural", always=True)
    def set_name_plural(cls, name_plural: str, values: dict[str, str]) -> str:
        """Set the plural name if no value was supplied."""
        return name_plural if name_plural else values.get("name", "") + "s"

    @validator("measured_attribute")
    def check_measured_attribute(cls, measured_attribute: str, values) -> str:
        """Check that the measured attribute is a valid attribute with a number type."""
        attributes = {attribute.key: attribute.type for attribute in values.get("attributes", [])}
        if measured_attribute and measured_attribute not in attributes:
            msg = f"Measured attribute {measured_attribute} is not an attribute of entity {values.get('name')}"
            raise ValueError(msg)
        if attributes[measured_attribute] not in (EntityAttributeType.FLOAT, EntityAttributeType.INTEGER):
            msg = f"Measured attribute {measured_attribute} does not have a number type"
            raise ValueError(msg)
        return measured_attribute


class Entities(MappedModel[Entity]):
    """Entity mapping."""
