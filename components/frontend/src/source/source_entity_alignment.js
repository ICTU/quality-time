import { alignmentPropType, entityAttributeTypePropType } from "../sharedPropTypes"

export function alignment(attributeType, attributeAlignment) {
    if (attributeAlignment === "left" || attributeAlignment === "right") {
        return attributeAlignment
    }
    // The attribute has no explicitly set alignment, use the attribute type to determine the alignment
    return {
        boolean: "left",
        date: "left",
        datetime: "left",
        float: "right",
        integer: "right",
        integer_percentage: "right",
        minutes: "right",
        text: "left",
    }[attributeType]
}
alignment.propTypes = {
    attributeType: entityAttributeTypePropType,
    attributeAlignment: alignmentPropType,
}
