import { string } from "prop-types"

import { StatusIcon } from "../measurement/StatusIcon"
import { childrenPropType, entityAttributePropType, entityPropType } from "../sharedPropTypes"
import { formatMetricValue } from "../utils"
import { HyperLink } from "../widgets/HyperLink"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

function formatBoolean(value) {
    return value.toLowerCase() === "true" ? "✅" : ""
}
formatBoolean.propTypes = {
    value: string.isRequired,
}

function DateAttribute({ cellContents, type }) {
    return <TimeAgoWithDate dateFirst noTime={type === "date"} date={cellContents} />
}
DateAttribute.propTypes = {
    cellContents: string.isRequired,
    type: string.isRequired,
}

function PreWrapped({ children }) {
    return (
        <pre data-testid="pre-wrapped" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            {children}
        </pre>
    )
}
PreWrapped.propTypes = {
    children: childrenPropType,
}

function BreakWord({ children }) {
    return <div style={{ wordBreak: "break-word" }}>{children}</div>
}
BreakWord.propTypes = {
    children: childrenPropType,
}

export function SourceEntityAttribute({ entity, entityAttribute }) {
    let cellContents = entity[entityAttribute.key] ?? ""
    // See the data model (components/shared_code/src/shared_data_model/meta/entity.py) for possible entity attribute
    // types. Note that if entity attribute types are removed old types need to be supported to allow for time travel.
    const type = entityAttribute.type ?? ""
    if (cellContents) {
        if (type.includes("integer")) {
            cellContents = formatMetricValue("count", cellContents)
        }
        if (type.includes("percentage")) {
            cellContents = cellContents + "%"
        }
        if (type.includes("date")) {
            cellContents = <DateAttribute cellContents={cellContents} type={type} />
        }
        if (type === "float") {
            const number = Math.round(10 * Number(cellContents)) / 10
            cellContents = number.toLocaleString(undefined, { useGrouping: true })
        }
        if (type === "status") {
            cellContents = <StatusIcon status={cellContents} />
        }
    }
    if (type === "boolean") {
        cellContents = formatBoolean(cellContents)
    }
    if (entity[entityAttribute.url]) {
        cellContents = <HyperLink url={entity[entityAttribute.url]}>{cellContents}</HyperLink>
    }
    return entityAttribute.pre ? <PreWrapped>{cellContents}</PreWrapped> : <BreakWord>{cellContents}</BreakWord>
}
SourceEntityAttribute.propTypes = {
    entity: entityPropType,
    entityAttribute: entityAttributePropType,
}
