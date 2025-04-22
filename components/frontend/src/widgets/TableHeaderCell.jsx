import { TableCell, TableSortLabel, Tooltip } from "@mui/material"
import { func, string } from "prop-types"

import {
    alignmentPropType,
    childrenPropType,
    labelPropType,
    popupContentPropType,
    sortDirectionPropType,
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
    children,
    colSpan,
    column,
    sortColumn,
    sortDirection,
    handleSort,
    label,
    textAlign,
    help,
}) {
    const sorted = sortColumn === column ? MuiSortDirection(sortDirection) : null
    return (
        <TableCell align={textAlign || "left"} colSpan={colSpan} sortDirection={sorted}>
            <TableSortLabel
                active={column === sortColumn}
                direction={column === sortColumn ? MuiSortDirection(sortDirection) : "asc"}
                onClick={() => handleSort(column)}
                sx={{
                    padding: "4px",
                    "&:focus": {
                        borderRadius: 2,
                        backgroundColor: "divider",
                    },
                }}
            >
                {children || <TableHeaderCellContents help={help} label={label} />}
            </TableSortLabel>
        </TableCell>
    )
}
SortableTableHeaderCell.propTypes = {
    children: childrenPropType,
    colSpan: string,
    column: string,
    handleSort: func,
    help: popupContentPropType,
    label: labelPropType,
    sortColumn: string,
    sortDirection: sortDirectionPropType,
    textAlign: alignmentPropType,
}

export function UnsortableTableHeaderCell({ colSpan, help, label, textAlign, width }) {
    return (
        <TableCell align={textAlign} colSpan={colSpan} width={width}>
            <TableHeaderCellContents help={help} label={label} />
        </TableCell>
    )
}
UnsortableTableHeaderCell.propTypes = {
    colSpan: string,
    help: popupContentPropType,
    label: labelPropType,
    textAlign: string,
    width: string,
}
