import "./SourceEntities.css"

import { func, string } from "prop-types"
import { useContext, useState } from "react"

import { DataModel } from "../context/DataModel"
import { Button, Icon, Popup, Table } from "../semantic_ui_react_wrappers"
import { entityPropType, metricPropType, reportPropType, sourcePropType } from "../sharedPropTypes"
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
    attributeType: string,
    attributeAligment: string,
}

export function SourceEntities({ metric, metric_uuid, reload, report, source }) {
    const dataModel = useContext(DataModel)
    const [hideIgnoredEntities, setHideIgnoredEntities] = useState(false)
    const [sortColumn, setSortColumn] = useState(null)
    const [columnType, setColumnType] = useState("text")
    const [sortDirection, setSortDirection] = useState("ascending")

    function sort(column, column_type) {
        setColumnType(column_type || "text")
        if (column === sortColumn) {
            setSortDirection(sortDirection === "ascending" ? "descending" : "ascending")
        } else {
            setSortColumn(column)
        }
    }
    function sorted(column) {
        return column === sortColumn ? sortDirection : null
    }

    const report_source = metric.sources[source.source_uuid]
    const source_type = report_source.type
    const metric_entities = dataModel.sources[source_type].entities[metric.type]
    if (!metric_entities || !Array.isArray(source.entities) || source.entities.length === 0) {
        return null
    }
    const entity_attributes = metric_entities.attributes.filter(
        (attribute) => attribute.visible === undefined || attribute.visible,
    )
    const entity_name = metric_entities.name
    const entity_name_plural = metric_entities.name_plural
    const headers = (
        <Table.Row>
            <Table.HeaderCell collapsing textAlign="center">
                <Popup
                    trigger={
                        <Button
                            basic
                            compact
                            icon={hideIgnoredEntities ? "unhide" : "hide"}
                            onClick={() => setHideIgnoredEntities(!hideIgnoredEntities)}
                            primary
                        />
                    }
                    content={
                        hideIgnoredEntities
                            ? `Show resolved ${entity_name_plural}`
                            : `Hide resolved ${entity_name_plural}`
                    }
                />
            </Table.HeaderCell>
            <Table.HeaderCell sorted={sorted("entity_status")} onClick={() => sort("entity_status")}>
                {`${capitalize(entity_name)} status`}
            </Table.HeaderCell>
            <Table.HeaderCell sorted={sorted("status_end_date")} onClick={() => sort("status_end_date")}>
                Status end date
            </Table.HeaderCell>
            <Table.HeaderCell sorted={sorted("rationale")} onClick={() => sort("rationale")}>
                Status rationale
            </Table.HeaderCell>
            <Table.HeaderCell onClick={() => sort("first_seen", "datetime")} sorted={sorted("first_seen")}>
                {capitalize(entity_name)} first seen
            </Table.HeaderCell>
            {entity_attributes.map((entity_attribute) => (
                <Table.HeaderCell
                    key={entity_attribute.key}
                    onClick={() => sort(entity_attribute.key, entity_attribute.type)}
                    sorted={sorted(entity_attribute.key)}
                    textAlign={alignment(entity_attribute.type, entity_attribute.alignment)}
                >
                    <span>{entity_attribute.name}</span>
                    {entity_attribute.help ? (
                        <Popup
                            on={["hover", "focus"]}
                            trigger={
                                <span>
                                    &nbsp;
                                    <Icon role="tooltip" aria-label="help" tabIndex="0" name="help circle" />
                                </span>
                            }
                            content={entity_attribute.help}
                        />
                    ) : null}
                </Table.HeaderCell>
            ))}
        </Table.Row>
    )
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
    const rows = entities.map((entity) => (
        <SourceEntity
            entity={entity}
            entity_attributes={entity_attributes}
            entity_name={entity_name}
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
