import { TableCell } from "@mui/material"
import { bool, func, string } from "prop-types"
import { useState } from "react"

import {
    entityAttributesPropType,
    entityPropType,
    entityUserDataPropType,
    reportPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { DivWithHtml } from "../widgets/DivWithHtml"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"
import { alignment } from "./source_entity_alignment"
import { entityCanBeIgnored, SOURCE_ENTITY_STATUS_NAME } from "./source_entity_status"
import { SourceEntityAttribute } from "./SourceEntityAttribute"
import { SourceEntityDetails } from "./SourceEntityDetails"

export function SourceEntity({
    columnsToHide,
    metricUuid,
    sourceUuid,
    hideIgnoredEntities,
    entity,
    entityName,
    entityAttributes,
    entityUserData,
    reload,
    report,
}) {
    const [expanded, setExpanded] = useState(false)

    const { rationale, status, statusEndDate } = entityUserData
    const ignoredEntity = entityCanBeIgnored(status, statusEndDate)
    if (hideIgnoredEntities && ignoredEntity) {
        return null
    }
    const style = ignoredEntity ? { textDecoration: "line-through" } : {}
    style["maxWidth"] = "60em"
    let statusClassName = "unknown_status"
    for (let entityAttribute of entityAttributes) {
        let cellContents = entity[entityAttribute.key]
        if (entityAttribute.color?.[cellContents]) {
            statusClassName = entityAttribute.color[cellContents] + "_status"
            break
        }
    }
    const details = (
        <SourceEntityDetails
            entity={entity}
            entityUserData={entityUserData}
            metricUuid={metricUuid}
            name={entityName}
            reload={reload}
            report={report}
            sourceUuid={sourceUuid}
        />
    )
    return (
        <TableRowWithDetails
            className={statusClassName}
            color={statusClassName}
            details={details}
            expanded={expanded}
            id={entity.key}
            key={entity.key}
            onExpand={setExpanded}
            style={{ maxHeight: "100px", overflow: "auto" }}
            firstCellContent={SOURCE_ENTITY_STATUS_NAME[status]}
            firstCellProps={{ colSpan: 2, sx: { paddingLeft: "6px", ...style } }}
        >
            {!columnsToHide.includes("status_end_date") && (
                <TableCell sx={style}>
                    {status === "unconfirmed" ? "" : <TimeAgoWithDate dateFirst noTime date={statusEndDate} />}
                </TableCell>
            )}
            {!columnsToHide.includes("rationale") && (
                <TableCell sx={style}>
                    <DivWithHtml>{rationale}</DivWithHtml>
                </TableCell>
            )}
            <TableCell sx={style}>
                {entity.first_seen ? <TimeAgoWithDate dateFirst date={entity.first_seen} /> : ""}
            </TableCell>
            {entityAttributes.map((entityAttribute) => (
                <TableCell
                    align={alignment(entityAttribute.type, entityAttribute.alignment)}
                    key={entityAttribute.key}
                    sx={style}
                >
                    <SourceEntityAttribute entity={entity} entityAttribute={entityAttribute} />
                </TableCell>
            ))}
        </TableRowWithDetails>
    )
}
SourceEntity.propTypes = {
    columnsToHide: stringsPropType,
    metricUuid: string,
    sourceUuid: string,
    hideIgnoredEntities: bool,
    entity: entityPropType,
    entityName: string,
    entityAttributes: entityAttributesPropType,
    entityUserData: entityUserDataPropType,
    reload: func,
    report: reportPropType,
}
