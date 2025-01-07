import { TableCell, TableSortLabel, Tooltip } from "@mui/material"
import { func, string } from "prop-types"

import {
    alignmentPropType,
    labelPropType,
    popupContentPropType,
    sortDirectionURLSearchQueryPropType,
    stringURLSearchQueryPropType,
} from "../sharedPropTypes"

function TableHeaderCellContents({ help, label }) {
    return help ? (
        <Tooltip slotProps={{ tooltip: { sx: { maxWidth: "30em" } } }} title={help}>
            <span>{label}</span>
        </Tooltip>
    ) : (
        label
    )
}
TableHeaderCellContents.propTypes = {
    help: popupContentPropType,
    label: labelPropType,
}

function MuiSortDirection(sortDirection) {
    return sortDirection === "ascending" ? "asc" : "desc"
}

export function SortableTableHeaderCell({
    colSpan,
    column,
    sortColumn,
    sortDirection,
    handleSort,
    label,
    textAlign,
    help,
}) {
    const sorted = sortColumn.value === column ? MuiSortDirection(sortDirection.value) : null
    return (
        <TableCell align={textAlign || "left"} colSpan={colSpan} sortDirection={sorted}>
            <TableSortLabel
                active={column === sortColumn.value}
                direction={column === sortColumn.value ? MuiSortDirection(sortDirection.value) : "asc"}
                onClick={() => handleSort(column)}
            >
                <TableHeaderCellContents help={help} label={label} />
            </TableSortLabel>
        </TableCell>
    )
}
SortableTableHeaderCell.propTypes = {
    colSpan: string,
    column: string,
    handleSort: func,
    help: popupContentPropType,
    label: labelPropType,
    sortColumn: stringURLSearchQueryPropType,
    sortDirection: sortDirectionURLSearchQueryPropType,
    textAlign: alignmentPropType,
}

export function UnsortableTableHeaderCell({ help, label, textAlign, width }) {
    return (
        <TableCell align={textAlign} width={width}>
            <TableHeaderCellContents help={help} label={label} />
        </TableCell>
    )
}
UnsortableTableHeaderCell.propTypes = {
    help: popupContentPropType,
    label: labelPropType,
    textAlign: string,
    width: string,
}
