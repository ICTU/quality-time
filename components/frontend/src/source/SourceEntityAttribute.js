import { string } from "prop-types"

import { StatusIcon } from "../measurement/StatusIcon"
import { entityPropType } from "../sharedPropTypes"
import { formatMetricValue } from "../utils"
import { HyperLink } from "../widgets/HyperLink"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

export function SourceEntityAttribute({ entity, entityAttribute }) {
    let cellContents = entity[entityAttribute.key] ?? ""
    if (typeof cellContents === "string" && cellContents.length >= 250) {
        cellContents = cellContents.slice(0, 247) + "..."
    }
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
        if (type === "datetime") {
            cellContents = <TimeAgoWithDate dateFirst date={cellContents} />
        }
        if (type === "date") {
            cellContents = <TimeAgoWithDate dateFirst noTime date={cellContents} />
        }
        if (type === "status") {
            cellContents = <StatusIcon status={cellContents} />
        }
    }
    if (entity[entityAttribute.url]) {
        cellContents = <HyperLink url={entity[entityAttribute.url]}>{cellContents}</HyperLink>
    }
    if (entityAttribute.pre) {
        return (
            <pre data-testid="pre-wrapped" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {cellContents}
            </pre>
        )
    }
    return <div style={{ wordBreak: "break-word" }}>{cellContents}</div>
}
SourceEntityAttribute.propTypes = {
    entity: entityPropType,
    entityAttribute: string,
}
