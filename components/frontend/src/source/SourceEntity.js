import "./SourceEntity.css"

import { bool, func, string } from "prop-types"
import { useState } from "react"
import { Table } from "semantic-ui-react"

import { entityAttributesPropType, entityPropType, entityStatusPropType, reportPropType } from "../sharedPropTypes"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"
import { IGNORABLE_SOURCE_ENTITY_STATUSES, SOURCE_ENTITY_STATUS_NAME } from "./source_entity_status"
import { alignment } from "./SourceEntities"
import { SourceEntityAttribute } from "./SourceEntityAttribute"
import { SourceEntityDetails } from "./SourceEntityDetails"

function entityCanBeIgnored(status, statusEndDateString) {
    const statusEndDate = new Date(statusEndDateString)
    const now = new Date()
    if (statusEndDate < now) {
        return false
    }
    return IGNORABLE_SOURCE_ENTITY_STATUSES.includes(status)
}
entityCanBeIgnored.propTypes = {
    status: entityStatusPropType,
    statusEndDateString: string,
}

export function SourceEntity({
    metric_uuid,
    source_uuid,
    hide_ignored_entities,
    entity,
    entity_name,
    entity_attributes,
    rationale,
    reload,
    report,
    status,
    status_end_date,
}) {
    const [expanded, setExpanded] = useState(false)

    const ignoredEntity = entityCanBeIgnored(status, status_end_date)
    if (hide_ignored_entities && ignoredEntity) {
        return null
    }
    const style = ignoredEntity ? { textDecoration: "line-through" } : {}
    style["maxWidth"] = "60em"
    let statusClassName = "unknown_status"
    for (let entity_attribute of entity_attributes) {
        let cellContents = entity[entity_attribute.key]
        if (entity_attribute.color?.[cellContents]) {
            statusClassName = entity_attribute.color[cellContents] + "_status"
            break
        }
    }
    const details = (
        <SourceEntityDetails
            entity={entity}
            metric_uuid={metric_uuid}
            name={entity_name}
            rationale={rationale}
            reload={reload}
            report={report}
            source_uuid={source_uuid}
            status={status}
            status_end_date={status_end_date}
        />
    )
    return (
        <TableRowWithDetails
            className={statusClassName}
            details={details}
            key={entity.key}
            expanded={expanded}
            onExpand={setExpanded}
        >
            <Table.Cell style={style}>{SOURCE_ENTITY_STATUS_NAME[status]}</Table.Cell>
            <Table.Cell style={style}>{status === "unconfirmed" ? "" : status_end_date}</Table.Cell>
            <Table.Cell style={style}>{rationale}</Table.Cell>
            <Table.Cell style={style}>
                {entity.first_seen ? <TimeAgoWithDate dateFirst date={entity.first_seen} /> : ""}
            </Table.Cell>
            {entity_attributes.map((entity_attribute) => (
                <Table.Cell
                    key={entity_attribute.key}
                    style={style}
                    textAlign={alignment(entity_attribute.type, entity_attribute.alignment)}
                >
                    <SourceEntityAttribute entity={entity} entityAttribute={entity_attribute} />
                </Table.Cell>
            ))}
        </TableRowWithDetails>
    )
}
SourceEntity.propTypes = {
    metric_uuid: string,
    source_uuid: string,
    hide_ignored_entities: bool,
    entity: entityPropType,
    entity_name: string,
    entity_attributes: entityAttributesPropType,
    rationale: string,
    reload: func,
    report: reportPropType,
    status: entityStatusPropType,
    status_end_date: string,
}
