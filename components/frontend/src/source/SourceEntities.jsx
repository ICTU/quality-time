import "./SourceEntities.css"

import HelpIcon from "@mui/icons-material/Help"
import {
    Badge,
    IconButton,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableFooter,
    TableHead,
    TablePagination,
    TableRow,
    TextField,
    Tooltip,
    Typography,
} from "@mui/material"
import { bool, func, number, object, string } from "prop-types"
import { useContext, useState } from "react"

import { DataModelContext } from "../context/DataModel"
import { zIndexInnerTableHeader } from "../defaults"
import {
    entityAttributePropType,
    entityAttributesPropType,
    entityAttributeTypePropType,
    loadingPropType,
    measurementsPropType,
    metricPropType,
    reportPropType,
    settingsPropType,
    sortDirectionPropType,
    sourcePropType,
    stringsPropType,
} from "../sharedPropTypes"
import { capitalize, getMetricUnit, getSourceTypeName } from "../utils"
import { IgnoreIcon, ShowIcon } from "../widgets/icons"
import { LoadingPlaceHolder } from "../widgets/Placeholder"
import { SortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { FailedToLoadMeasurementsWarningMessage, InfoMessage } from "../widgets/WarningMessage"
import { alignment } from "./source_entity_alignment"
import { determineColumnsToHide } from "./source_entity_column"
import {
    entityCanBeIgnored,
    entityStatus,
    entityStatusEndDate,
    entityStatusRationale,
    entityUserData,
    SOURCE_ENTITY_STATUS_NAME,
} from "./source_entity_status"
import { SourceEntity } from "./SourceEntity"

function EntityAttributeHeaderCell({ entityAttribute, ...sortProps }) {
    return (
        <SortableTableHeaderCell
            column={entityAttribute.key}
            handleSort={sortProps.handleSort}
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
    handleSort: func,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
}

function sourceEntitiesHeaders(
    columnsToHide,
    entityAttributes,
    hideIgnoredEntities,
    metricEntities,
    nrIgnoredEntities,
    toggleHideIgnoredEntities,
    sortProps,
) {
    const action = hideIgnoredEntities ? "Show" : "Hide"
    const entityNameSingular = metricEntities.name
    const entityNamePlural = metricEntities.name_plural
    const entityNameOrNames = nrIgnoredEntities === 1 ? entityNameSingular : entityNamePlural
    const hasOrHave = nrIgnoredEntities === 1 ? "has" : "have"
    const tooltip = `${action} the ${nrIgnoredEntities} ${entityNameOrNames} that ${hasOrHave} been marked as fixed, false positive, or won't fix.`
    return (
        <TableRow>
            <TableCell sx={{ paddingRight: "6px" }}>
                <Tooltip title={tooltip}>
                    <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                        <IconButton disabled={nrIgnoredEntities === 0} onClick={toggleHideIgnoredEntities}>
                            <Badge badgeContent={nrIgnoredEntities} color={"entity_status_count_badge"} showZero>
                                {hideIgnoredEntities ? <ShowIcon /> : <IgnoreIcon />}
                            </Badge>
                        </IconButton>
                    </span>
                </Tooltip>
            </TableCell>
            <SortableTableHeaderCell column="entity_status" {...sortProps}>
                {`${capitalize(entityNameSingular)} status`}
            </SortableTableHeaderCell>
            {!columnsToHide.includes("status_end_date") && (
                <SortableTableHeaderCell column="status_end_date" {...sortProps}>
                    Status end date
                </SortableTableHeaderCell>
            )}
            {!columnsToHide.includes("rationale") && (
                <SortableTableHeaderCell column="rationale" {...sortProps}>
                    Status rationale
                </SortableTableHeaderCell>
            )}
            <SortableTableHeaderCell column="first_seen" {...sortProps}>
                {capitalize(entityNameSingular)} first seen
            </SortableTableHeaderCell>
            {entityAttributes.map((entityAttribute) => (
                <EntityAttributeHeaderCell entityAttribute={entityAttribute} key={entityAttribute.key} {...sortProps} />
            ))}
        </TableRow>
    )
}
sourceEntitiesHeaders.propTypes = {
    columnsToHide: stringsPropType,
    entityAttributes: entityAttributesPropType,
    hideIgnoredEntities: bool,
    metricEntities: object,
    nrIgnoredEntities: number,
    toggleHideIgnoredEntities: func,
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
                integer: (entity) => Number.parseInt(entity[sortColumn], 10),
                integer_percentage: (entity) => Number.parseInt(entity[sortColumn], 10),
                float: (entity) => Number.parseFloat(entity[sortColumn]),
                date: (entity) => Date.parse(entity[sortColumn]),
                datetime: (entity) => Date.parse(entity[sortColumn]),
                minutes: (entity) => Number.parseInt(entity[sortColumn], 10),
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

const builtInEntityColumnTypes = {
    entity_status: "text",
    status_end_date: "date",
    rationale: "text",
    first_seen: "datetime",
}

function entityColumnType(column, entityAttributes) {
    return builtInEntityColumnTypes[column] ?? entityAttributes.find((a) => a.key === column)?.type ?? "text"
}

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50, 100]
const DEFAULT_ROWS_PER_PAGE_OPTION = 1 // Take the second option as default number of rows per page

function entityMatchesFilter(entity, entityAttributes, userData, filter) {
    const fields = [SOURCE_ENTITY_STATUS_NAME[userData.status], userData.rationale]
    fields.push(...entityAttributes.map((entityAttribute) => entity[entityAttribute.key]))
    return fields.join(" ").toLowerCase().includes(filter.toLowerCase())
}

function SourceEntitiesFooter({
    entityNamePlural,
    filter,
    nrFilteredEntities,
    nrUnhiddenEntities,
    onFilterChange,
    onPageChange,
    onRowsPerPageChange,
    page,
    rowsPerPage,
}) {
    if (nrUnhiddenEntities <= ROWS_PER_PAGE_OPTIONS[0]) {
        return null
    }
    return (
        <TableFooter
            sx={{
                bgcolor: "background.paper",
                bottom: 0,
                position: "sticky",
                zIndex: zIndexInnerTableHeader,
                "@media print": { display: "none" },
            }}
        >
            <TableRow>
                <TableCell colSpan={99}>
                    <Stack direction="row" sx={{ alignItems: "center", justifyContent: "space-between", pl: "8px" }}>
                        <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
                            <TextField
                                label={`Filter ${entityNamePlural}`}
                                onChange={(event) => onFilterChange(event.target.value)}
                                size="small"
                                type="search"
                                value={filter}
                            />
                            {filter && (
                                <Typography variant="body2">
                                    {`${nrFilteredEntities} of ${nrUnhiddenEntities} ${entityNamePlural} ${nrFilteredEntities === 1 ? "matches" : "match"}`}
                                </Typography>
                            )}
                        </Stack>
                        <TablePagination
                            component="div"
                            count={nrFilteredEntities}
                            onPageChange={(_event, newPage) => onPageChange(newPage)}
                            onRowsPerPageChange={(event) =>
                                onRowsPerPageChange(Number.parseInt(event.target.value, 10))
                            }
                            page={page}
                            rowsPerPage={rowsPerPage}
                            rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
                            showFirstButton
                            showLastButton
                        />
                    </Stack>
                </TableCell>
            </TableRow>
        </TableFooter>
    )
}
SourceEntitiesFooter.propTypes = {
    entityNamePlural: string,
    filter: string,
    nrFilteredEntities: number,
    nrUnhiddenEntities: number,
    onFilterChange: func,
    onPageChange: func,
    onRowsPerPageChange: func,
    page: number,
    rowsPerPage: number,
}

export function SourceEntities({ loading, measurements, metric, metricUuid, reload, report, settings, sourceUuid }) {
    const dataModel = useContext(DataModelContext)
    const [page, setPage] = useState(0)
    const [rowsPerPage, setRowsPerPage] = useState(ROWS_PER_PAGE_OPTIONS[DEFAULT_ROWS_PER_PAGE_OPTION])
    const [filter, setFilter] = useState("")
    const sortColumn = settings.entitySortColumn.getItem(metricUuid) || null
    const sortDirection = settings.entitySortDirection.getItem(metricUuid)

    const source = metric.sources[sourceUuid]
    const metricEntities = dataModel.sources[source.type]?.entities?.[metric.type]

    if (!metricEntities) {
        const unit = getMetricUnit(metric, dataModel) || "entities"
        return (
            <InfoMessage title="Measurement details not supported">
                {`Showing individual ${unit} is not supported when using ${getSourceTypeName(source, dataModel)} as source.`}
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
    const lastMeasurement = measurements.at(-1)
    const lastMeasurementSource = lastMeasurement.sources.find((source) => source.source_uuid === sourceUuid)
    if (!Array.isArray(lastMeasurementSource?.entities) || lastMeasurementSource.entities.length === 0) {
        return (
            <InfoMessage title="Measurement details not available">
                There are currently no measurement details available.
            </InfoMessage>
        )
    }
    const entityAttributes = metricEntities.attributes.filter((attribute) => attribute?.visible ?? true)
    function handleSort(column) {
        if (column === sortColumn) {
            const newDirection = sortDirection === "ascending" ? "descending" : "ascending"
            settings.entitySortDirection.setItem(metricUuid, newDirection)
        } else {
            settings.entitySortColumn.setItem(metricUuid, column)
        }
    }
    const sortProps = {
        handleSort: handleSort,
        sortColumn: sortColumn,
        sortDirection: sortDirection,
    }
    const columnType = sortColumn ? entityColumnType(sortColumn, entityAttributes) : "text"
    const entities = sortedEntities(columnType, sortColumn, sortDirection, lastMeasurementSource)
    const columnsToHide = determineColumnsToHide(settings, lastMeasurementSource, entities)
    const hideIgnoredEntities = settings.hideIgnoredEntities.includes(metricUuid)
    const isIgnored = (entity) =>
        entityCanBeIgnored(
            entityStatus(lastMeasurementSource, entity),
            entityStatusEndDate(lastMeasurementSource, entity),
        )
    const nrIgnoredEntities = entities.filter(isIgnored).length
    const unhiddenEntities = hideIgnoredEntities ? entities.filter((entity) => !isIgnored(entity)) : entities
    const filteredEntities = filter
        ? unhiddenEntities.filter((entity) =>
              entityMatchesFilter(entity, entityAttributes, entityUserData(lastMeasurementSource, entity), filter),
          )
        : unhiddenEntities
    // Make sure the current page still exists, e.g. after hiding ignored entities:
    const lastPage = Math.max(0, Math.ceil(filteredEntities.length / rowsPerPage) - 1)
    const currentPage = Math.min(page, lastPage)
    const firstIndex = currentPage * rowsPerPage
    // Render the entities on other pages as well, but only for printing, so exported PDFs contain all entities:
    const rows = filteredEntities.map((entity, index) => (
        <SourceEntity
            columnsToHide={columnsToHide}
            entity={entity}
            entityAttributes={entityAttributes}
            entityName={metricEntities.name}
            key={entity.key}
            metricUuid={metricUuid}
            printOnly={index < firstIndex || index >= firstIndex + rowsPerPage}
            reload={reload}
            entityUserData={entityUserData(lastMeasurementSource, entity)}
            report={report}
            sourceUuid={sourceUuid}
        />
    ))
    const headers = sourceEntitiesHeaders(
        columnsToHide,
        entityAttributes,
        hideIgnoredEntities,
        metricEntities,
        nrIgnoredEntities,
        () => settings.hideIgnoredEntities.toggle(metricUuid),
        sortProps,
    )
    return (
        <TableContainer sx={{ maxHeight: "50vh" }}>
            <Table padding="none" size="small" stickyHeader>
                <TableHead sx={{ zIndex: zIndexInnerTableHeader }}>{headers}</TableHead>
                <TableBody>{rows}</TableBody>
                <SourceEntitiesFooter
                    entityNamePlural={metricEntities.name_plural}
                    filter={filter}
                    nrFilteredEntities={filteredEntities.length}
                    nrUnhiddenEntities={unhiddenEntities.length}
                    onFilterChange={(newFilter) => {
                        setFilter(newFilter)
                        setPage(0)
                    }}
                    onPageChange={setPage}
                    onRowsPerPageChange={(newRowsPerPage) => {
                        setRowsPerPage(newRowsPerPage)
                        setPage(0)
                    }}
                    page={currentPage}
                    rowsPerPage={rowsPerPage}
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
    settings: settingsPropType,
    sourceUuid: string,
}
