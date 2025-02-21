"""Data model entities."""

from .meta.entity import Entity, EntityAttribute, EntityAttributeType

MERGE_REQUEST_ENTITY = Entity(
    name="merge request",
    attributes=[
        EntityAttribute(name="Merge request", key="title", url="url"),
        EntityAttribute(name="Target branch", key="target_branch"),
        EntityAttribute(name="State"),
        EntityAttribute(name="Upvotes", type=EntityAttributeType.INTEGER),
        EntityAttribute(name="Downvotes", type=EntityAttributeType.INTEGER),
        EntityAttribute(name="Created", type=EntityAttributeType.DATETIME),
        EntityAttribute(name="Closed", type=EntityAttributeType.DATETIME),
    ],
)
