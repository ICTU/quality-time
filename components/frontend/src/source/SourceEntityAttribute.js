import { StatusIcon } from "../measurement/StatusIcon"
import { HyperLink } from "../widgets/HyperLink"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

export function SourceEntityAttribute({ entity, entity_attribute }) {
    let cellContents = entity[entity_attribute.key] ?? ""
    if (typeof cellContents === "string" && cellContents.length >= 250) {
        cellContents = cellContents.slice(0, 247) + "..."
    }
    const type = entity_attribute.type ?? ""
    cellContents =
        cellContents && type === "datetime" ? <TimeAgoWithDate dateFirst date={cellContents} /> : cellContents
    cellContents =
        cellContents && type === "date" ? <TimeAgoWithDate dateFirst noTime date={cellContents} /> : cellContents
    cellContents = cellContents && type.includes("integer") ? Math.round(cellContents).toString() : cellContents
    cellContents = cellContents && type.includes("percentage") ? cellContents + "%" : cellContents
    cellContents = cellContents && type === "status" ? <StatusIcon status={cellContents} /> : cellContents
    cellContents = entity[entity_attribute.url] ? (
        <HyperLink url={entity[entity_attribute.url]}>{cellContents}</HyperLink>
    ) : (
        cellContents
    )
    cellContents = entity_attribute.pre ? (
        <pre data-testid="pre-wrapped" style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
            {cellContents}
        </pre>
    ) : (
        <div style={{ wordBreak: "break-word" }}>{cellContents}</div>
    )
    return cellContents
}
