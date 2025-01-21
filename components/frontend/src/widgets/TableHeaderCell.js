import { ButtonBase, TableCell, TableSortLabel, Tooltip } from "@mui/material"
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
    const align = textAlign || "left"
    return (
        <TableCell colSpan={colSpan} sortDirection={sorted}>
            <ButtonBase
                focusRipple
                sx={{
                    display: "block",
                    fontSize: "inherit",
                    padding: "inherit",
                    textAlign: align,
                    width: "100%",
                }}
                tabIndex={-1}
            >
                <TableSortLabel
                    active={column === sortColumn}
                    direction={column === sortColumn ? MuiSortDirection(sortDirection) : "asc"}
                    onClick={() => handleSort(column)}
                >
                    {children || <TableHeaderCellContents help={help} label={label} />}
                </TableSortLabel>
            </ButtonBase>
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
