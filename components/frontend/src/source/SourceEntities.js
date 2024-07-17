import "./SourceEntities.css"

import { bool, func, object, string } from "prop-types"
import { useContext, useState } from "react"

import { DataModel } from "../context/DataModel"
import { Button, Icon, Popup, Table } from "../semantic_ui_react_wrappers"
import {
    alignmentPropType,
    childrenPropType,
    entityAttributePropType,
    entityAttributesPropType,
    entityAttributeTypePropType,
    entityPropType,
    metricPropType,
    reportPropType,
    sortDirectionPropType,
    sourcePropType,
} from "../sharedPropTypes"
import { capitalize } from "../utils"
import { SourceEntity } from "./SourceEntity"

function entityStatus(source, entity) {
    return source.entity_user_data?.[entity.key]?.status ?? "unconfirmed"
}
entityStatus.propTypes = {
    source: sourcePropType,
    entity: entityPropType,
}

function entityStatusEndDate(source, entity) {
    return source.entity_user_data?.[entity.key]?.status_end_date ?? ""
}
entityStatusEndDate.propTypes = {
    source: sourcePropType,
    entity: entityPropType,
}

function entityStatusRationale(source, entity) {
    return source.entity_user_data?.[entity.key]?.rationale ?? ""
}
entityStatusRationale.propTypes = {
    source: sourcePropType,
    entity: entityPropType,
}

export function alignment(attributeType, attributeAlignment) {
    if (attributeAlignment === "left" || attributeAlignment === "right") {
        return attributeAlignment
    }
    // The attribute has no explicitly set aligment, use the attribute type to determine the alignment
    return {
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
    attributeAligment: alignmentPropType,
}

function sorted(column, sortColumn, sortDirection) {
    return column === sortColumn ? sortDirection : null
}
sorted.propTypes = {
    column: string,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
}

function sort(column, columnType, setColumnType, setSortColumn, setSortDirection, sortColumn, sortDirection) {
    setColumnType(columnType)
    if (column === sortColumn) {
        setSortDirection(sortDirection === "ascending" ? "descending" : "ascending")
    } else {
        setSortColumn(column)
    }
}
sort.propTypes = {
    column: string,
    columnType: entityAttributeTypePropType,
    setColumnType: func,
    setSortColumn: func,
    setSortDirection: func,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
}

function SortableHeaderCell({
    children,
    column,
    columnType,
    setColumnType,
    setSortColumn,
    setSortDirection,
    sortColumn,
    sortDirection,
    textAlign,
}) {
    return (
        <Table.HeaderCell
            onClick={() =>
                sort(column, columnType, setColumnType, setSortColumn, setSortDirection, sortColumn, sortDirection)
            }
            sorted={sorted(column, sortColumn, sortDirection)}
            textAlign={textAlign}
        >
            {children}
        </Table.HeaderCell>
    )
}
SortableHeaderCell.propTypes = {
    children: childrenPropType,
    column: string,
    columnType: entityAttributeTypePropType,
    setColumnType: func,
    setSortColumn: func,
    setSortDirection: func,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
    textAlign: alignmentPropType,
}

function EntityAttributeHeaderCell({ entityAttribute, ...sortProps }) {
    return (
        <SortableHeaderCell
            column={entityAttribute.key}
            columnType={entityAttribute.type || "text"}
            textAlign={alignment(entityAttribute.type, entityAttribute.alignment)}
            {...sortProps}
        >
            <span>{entityAttribute.name}</span>k
            {entityAttribute.help ? (
                <Popup
                    on={["hover", "focus"]}
                    trigger={
                        <span>
                            &nbsp;
                            <Icon role="tooltip" aria-label="help" tabIndex="0" name="help circle" />
                        </span>
                    }
                    content={entityAttribute.help}
                />
            ) : null}
        </SortableHeaderCell>
    )
}
EntityAttributeHeaderCell.propTypes = {
    entityAttribute: entityAttributePropType,
    setColumnType: func,
    setSortColumn: func,
    setSortDirection: func,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
}

function sourceEntitiesHeaders(
    entityAttributes,
    hideIgnoredEntities,
    metricEntities,
    setHideIgnoredEntities,
    sortProps,
) {
    const entityName = metricEntities.name
    const entityNamePlural = metricEntities.name_plural
    const hideIgnoredEntitiesLabel = `${hideIgnoredEntities ? "Show" : "Hide"} resolved ${entityNamePlural}`
    return (
        <Table.Row>
            <Table.HeaderCell collapsing textAlign="center">
                <Popup
                    trigger={
                        <Button
                            aria-label={hideIgnoredEntitiesLabel}
                            basic
                            compact
                            icon={hideIgnoredEntities ? "unhide" : "hide"}
                            onClick={() => setHideIgnoredEntities(!hideIgnoredEntities)}
                            primary
                        />
                    }
                    content={hideIgnoredEntitiesLabel}
                />
            </Table.HeaderCell>
            <SortableHeaderCell column="entity_status" columnType="text" {...sortProps}>
                {`${capitalize(entityName)} status`}
            </SortableHeaderCell>
            <SortableHeaderCell column="status_end_date" columnType="date" {...sortProps}>
                Status end date
            </SortableHeaderCell>
            <SortableHeaderCell column="rationale" columnType="text" {...sortProps}>
                Status rationale
            </SortableHeaderCell>
            <SortableHeaderCell column="first_seen" columnType="datetime" {...sortProps}>
                ${capitalize(entityName)} first seen
            </SortableHeaderCell>
            {entityAttributes.map((entityAttribute) => (
                <EntityAttributeHeaderCell entityAttribute={entityAttribute} key={entityAttribute.key} {...sortProps} />
            ))}
        </Table.Row>
    )
}
sourceEntitiesHeaders.propTypes = {
    entityAttributes: entityAttributesPropType,
    hideIgnoredEntities: bool,
    metricEntities: object,
    setColumnType: func,
    setHideIgnoredEntities: func,
    setSortColumn: func,
    setSortDirection: func,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
}

function sortedEntities(columnType, sortColumn, sortDirection, source) {
    let entities = Array.from(source.entities)
    if (sortColumn !== null) {
        let parse
        if (sortColumn === "entity_status") {
            parse = (entity) => entityStatus(source, entity)
        } else if (sortColumn === "status_end_date") {
            parse = (entity) =>
                entityStatus(source, entity) === "unconfirmed" ? "" : entityStatusEndDate(source, entity)
        } else if (sortColumn === "rationale") {
            parse = (entity) =>
                entityStatus(source, entity) === "unconfirmed" ? "" : entityStatusRationale(source, entity)
        } else {
            parse = {
                integer: (entity) => parseInt(entity[sortColumn], 10),
                integer_percentage: (entity) => parseInt(entity[sortColumn], 10),
                float: (entity) => parseFloat(entity[sortColumn]),
                date: (entity) => Date.parse(entity[sortColumn]),
                datetime: (entity) => Date.parse(entity[sortColumn]),
                minutes: (entity) => parseInt(entity[sortColumn], 10),
                text: (entity) => entity[sortColumn],
            }[columnType]
        }
        entities.sort((a, b) => (parse(a) < parse(b) ? -1 : 1))
        if (sortDirection === "descending") {
            entities.reverse()
        }
    }
    return entities
}
sortedEntities.propTypes = {
    columnType: entityAttributeTypePropType,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
    source: sourcePropType,
}

export function SourceEntities({ metric, metric_uuid, reload, report, source }) {
    const dataModel = useContext(DataModel)
    const [hideIgnoredEntities, setHideIgnoredEntities] = useState(false)
    const [sortColumn, setSortColumn] = useState(null)
    const [columnType, setColumnType] = useState("text")
    const [sortDirection, setSortDirection] = useState("ascending")

    const reportSource = metric.sources[source.source_uuid]
    const metricEntities = dataModel.sources[reportSource.type].entities[metric.type]
    if (!metricEntities || !Array.isArray(source.entities) || source.entities.length === 0) {
        return null
    }
    const entityAttributes = metricEntities.attributes.filter((attribute) => attribute?.visible ?? true)
    const sortProps = {
        setColumnType: setColumnType,
        setSortColumn: setSortColumn,
        setSortDirection: setSortDirection,
        sortColumn: sortColumn,
        sortDirection: sortDirection,
    }
    const headers = sourceEntitiesHeaders(
        entityAttributes,
        hideIgnoredEntities,
        metricEntities,
        setHideIgnoredEntities,
        sortProps,
    )
    const entities = sortedEntities(columnType, sortColumn, sortDirection, source)
    const rows = entities.map((entity) => (
        <SourceEntity
            entity={entity}
            entity_attributes={entityAttributes}
            entity_name={metricEntities.name}
            hide_ignored_entities={hideIgnoredEntities}
            key={entity.key}
            metric_uuid={metric_uuid}
            reload={reload}
            report={report}
            status={entityStatus(source, entity)}
            status_end_date={entityStatusEndDate(source, entity)}
            rationale={entityStatusRationale(source, entity)}
            source_uuid={source.source_uuid}
        />
    ))
    return (
        <Table className="entities stickyHeader" sortable size="small">
            <Table.Header>{headers}</Table.Header>
            <Table.Body>{rows}</Table.Body>
        </Table>
    )
}
SourceEntities.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
    source: sourcePropType,
}
