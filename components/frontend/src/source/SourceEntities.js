import "./SourceEntities.css"

import HelpIcon from "@mui/icons-material/Help"
import {
    IconButton,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tooltip,
} from "@mui/material"
import { bool, func, object, string } from "prop-types"
import { useContext, useState } from "react"

import { DataModel } from "../context/DataModel"
import {
    alignmentPropType,
    entityAttributePropType,
    entityAttributesPropType,
    entityAttributeTypePropType,
    entityPropType,
    loadingPropType,
    measurementsPropType,
    metricPropType,
    reportPropType,
    sortDirectionPropType,
    sourcePropType,
} from "../sharedPropTypes"
import { capitalize } from "../utils"
import { IgnoreIcon, ShowIcon } from "../widgets/icons"
import { LoadingPlaceHolder } from "../widgets/Placeholder"
import { SortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { FailedToLoadMeasurementsWarningMessage, InfoMessage } from "../widgets/WarningMessage"
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
    // The attribute has no explicitly set alignment, use the attribute type to determine the alignment
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
    attributeAlignment: alignmentPropType,
}

function sorted(column, sortColumn, sortDirection) {
    return column === sortColumn ? sortDirection : null
}
sorted.propTypes = {
    column: string,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
}

function EntityAttributeHeaderCell({ entityAttribute, ...sortProps }) {
    function handleSort(column) {
        sortProps.setColumnType(entityAttribute.type || "text")
        if (column === sortProps.sortColumn) {
            sortProps.setSortDirection(sortProps.sortDirection === "ascending" ? "descending" : "ascending")
        } else {
            sortProps.setSortColumn(column)
        }
    }
    return (
        <SortableTableHeaderCell
            column={entityAttribute.key}
            handleSort={handleSort}
            textAlign={alignment(entityAttribute.type, entityAttribute.alignment)}
            {...sortProps}
        >
            <span>{entityAttribute.name}</span>
            {entityAttribute.help ? (
                <Tooltip title={entityAttribute.help}>
                    <span>
                        &nbsp;
                        <HelpIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} tabIndex="0" />
                    </span>
                </Tooltip>
            ) : null}
        </SortableTableHeaderCell>
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
    const hideIgnoredEntitiesLabel = `${hideIgnoredEntities ? "Show" : "Hide"} ignored ${entityNamePlural}`
    function handleSort(column, columnType) {
        sortProps.setColumnType(columnType)
        if (column === sortProps.sortColumn) {
            sortProps.setSortDirection(sortProps.sortDirection === "ascending" ? "descending" : "ascending")
        } else {
            sortProps.setSortColumn(column)
        }
    }
    return (
        <TableRow>
            <TableCell align="center">
                <Tooltip title={hideIgnoredEntitiesLabel}>
                    <IconButton
                        aria-label={hideIgnoredEntitiesLabel}
                        onClick={() => setHideIgnoredEntities(!hideIgnoredEntities)}
                    >
                        {hideIgnoredEntities ? <ShowIcon /> : <IgnoreIcon />}
                    </IconButton>
                </Tooltip>
            </TableCell>
            <SortableTableHeaderCell
                column="entity_status"
                handleSort={(column) => handleSort(column, "text")}
                {...sortProps}
            >
                {`${capitalize(entityName)} status`}
            </SortableTableHeaderCell>
            <SortableTableHeaderCell
                column="status_end_date"
                handleSort={(column) => handleSort(column, "date")}
                {...sortProps}
            >
                Status end date
            </SortableTableHeaderCell>
            <SortableTableHeaderCell
                column="rationale"
                handleSort={(column) => handleSort(column, "text")}
                {...sortProps}
            >
                Status rationale
            </SortableTableHeaderCell>
            <SortableTableHeaderCell
                column="first_seen"
                handleSort={(column) => handleSort(column, "datetime")}
                {...sortProps}
            >
                {capitalize(entityName)} first seen
            </SortableTableHeaderCell>
            {entityAttributes.map((entityAttribute) => (
                <EntityAttributeHeaderCell entityAttribute={entityAttribute} key={entityAttribute.key} {...sortProps} />
            ))}
        </TableRow>
    )
}
sourceEntitiesHeaders.propTypes = {
    entityAttributes: entityAttributesPropType,
    hideIgnoredEntities: bool,
    metricEntities: object,
    setHideIgnoredEntities: func,
    sortProps: object,
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

export function SourceEntities({ loading, measurements, metric, metric_uuid, reload, report, source_uuid }) {
    const dataModel = useContext(DataModel)
    const [hideIgnoredEntities, setHideIgnoredEntities] = useState(false)
    const [sortColumn, setSortColumn] = useState(null)
    const [columnType, setColumnType] = useState("text")
    const [sortDirection, setSortDirection] = useState("ascending")

    const sourceType = metric.sources[source_uuid].type
    const metricEntities = dataModel.sources[sourceType]?.entities?.[metric.type]

    if (!metricEntities) {
        const unit = dataModel.metrics[metric.type].unit || "entities"
        const sourceTypeName = dataModel.sources[sourceType].name
        return (
            <InfoMessage title="Measurement details not supported">
                {`Showing individual ${unit} is not supported when using ${sourceTypeName} as source.`}
            </InfoMessage>
        )
    }
    if (loading === "failed") {
        return <FailedToLoadMeasurementsWarningMessage />
    }
    if (loading === "loading") {
        return <LoadingPlaceHolder />
    }
    if (measurements.length === 0) {
        return (
            <InfoMessage title="No measurements available">
                Measurement details not available because Quality-time has not collected any measurements yet.
            </InfoMessage>
        )
    }
    const lastMeasurement = measurements[measurements.length - 1]
    const source = lastMeasurement.sources.find((source) => source.source_uuid === source_uuid)
    if (!Array.isArray(source.entities) || source.entities.length === 0) {
        return (
            <InfoMessage title="Measurement details not available">
                There are currently no measurement details available.
            </InfoMessage>
        )
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
        <TableContainer component={Paper} sx={{ maxHeight: "50vh" }}>
            <Table padding="none" size="small">
                <TableHead>{headers}</TableHead>
                <TableBody>{rows}</TableBody>
            </Table>
        </TableContainer>
    )
}
SourceEntities.propTypes = {
    loading: loadingPropType,
    measurements: measurementsPropType,
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
    source_uuid: string,
}
