import "./SourceEntities.css"

import HelpIcon from "@mui/icons-material/Help"
import { Table, TableBody, TableCell, TableContainer, TableFooter, TableHead, TableRow, Tooltip } from "@mui/material"
import { bool, func, object, string } from "prop-types"
import { useContext, useState } from "react"

import { DataModel } from "../context/DataModel"
import { zIndexInnerTableHeader } from "../defaults"
import {
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
import { ButtonRow } from "../widgets/ButtonRow"
import { ActionButton } from "../widgets/buttons/ActionButton"
import { IgnoreIcon, ShowIcon } from "../widgets/icons"
import { LoadingPlaceHolder } from "../widgets/Placeholder"
import { SortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { FailedToLoadMeasurementsWarningMessage, InfoMessage } from "../widgets/WarningMessage"
import { alignment } from "./source_entity_alignment"
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
            {entityAttribute.help ? (
                <Tooltip title={entityAttribute.help}>
                    {entityAttribute.name}
                    <HelpIcon fontSize="inherit" sx={{ marginLeft: "1em", verticalAlign: "middle" }} tabIndex="0" />
                </Tooltip>
            ) : (
                <span>{entityAttribute.name}</span>
            )}
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

function sourceEntitiesHeaders(entityAttributes, metricEntities, sortProps) {
    const entityName = metricEntities.name
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
    metricEntities: object,
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
                boolean: (entity) => entity[sortColumn],
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

function Footer({ entityNamePlural, hideIgnoredEntities, setHideIgnoredEntities }) {
    const action = hideIgnoredEntities ? "Show" : "Hide"
    const hideIgnoredEntitiesTooltip = `${action} ${entityNamePlural} that have been marked as fixed, false positive, or won't fix.`
    return (
        <TableFooter>
            <TableRow>
                <TableCell colSpan={99}>
                    <ButtonRow paddingLeft={0} paddingRight={0}>
                        <ActionButton
                            action={hideIgnoredEntities ? "Show" : "Hide"}
                            itemType={`ignored ${entityNamePlural}`}
                            startIcon={hideIgnoredEntities ? <ShowIcon /> : <IgnoreIcon />}
                            onClick={() => setHideIgnoredEntities(!hideIgnoredEntities)}
                            popup={hideIgnoredEntitiesTooltip}
                        />
                    </ButtonRow>
                </TableCell>
            </TableRow>
        </TableFooter>
    )
}
Footer.propTypes = {
    entityNamePlural: string.isRequired,
    hideIgnoredEntities: bool.isRequired,
    setHideIgnoredEntities: func.isRequired,
}

export function SourceEntities({ loading, measurements, metric, metricUuid, reload, report, sourceUuid }) {
    const dataModel = useContext(DataModel)
    const [hideIgnoredEntities, setHideIgnoredEntities] = useState(false)
    const [sortColumn, setSortColumn] = useState(null)
    const [columnType, setColumnType] = useState("text")
    const [sortDirection, setSortDirection] = useState("ascending")

    const sourceType = metric.sources[sourceUuid].type
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
    const source = lastMeasurement.sources.find((source) => source.source_uuid === sourceUuid)
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
    const headers = sourceEntitiesHeaders(entityAttributes, metricEntities, sortProps)
    const entities = sortedEntities(columnType, sortColumn, sortDirection, source)
    const rows = entities.map((entity) => (
        <SourceEntity
            entity={entity}
            entityAttributes={entityAttributes}
            entityName={metricEntities.name}
            hideIgnoredEntities={hideIgnoredEntities}
            key={entity.key}
            metricUuid={metricUuid}
            reload={reload}
            report={report}
            status={entityStatus(source, entity)}
            statusEndDate={entityStatusEndDate(source, entity)}
            rationale={entityStatusRationale(source, entity)}
            sourceUuid={source.source_uuid}
        />
    ))
    const entityNamePlural = metricEntities.name_plural
    return (
        <TableContainer sx={{ maxHeight: "50vh" }}>
            <Table padding="none" size="small" stickyHeader>
                <TableHead sx={{ zIndex: zIndexInnerTableHeader }}>{headers}</TableHead>
                <TableBody>{rows}</TableBody>
                <Footer
                    entityNamePlural={entityNamePlural}
                    hideIgnoredEntities={hideIgnoredEntities}
                    setHideIgnoredEntities={setHideIgnoredEntities}
                />
            </Table>
        </TableContainer>
    )
}
SourceEntities.propTypes = {
    loading: loadingPropType,
    measurements: measurementsPropType,
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    report: reportPropType,
    sourceUuid: string,
}
