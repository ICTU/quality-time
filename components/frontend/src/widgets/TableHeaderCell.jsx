import { TableCell, TableSortLabel, Tooltip } from "@mui/material"
import PropTypes, { func, string } from "prop-types"

import {
    alignmentPropType,
    childrenPropType,
    labelPropType,
    popupContentPropType,
    sortDirectionPropType,
} from "../sharedPropTypes"

function TableHeaderCellContents({ help, label, icon }) {
    if (help && icon) {
        return (
            <Tooltip slotProps={{ tooltip: { sx: { maxWidth: "30em" } } }} title={help} disableInteractive>
                <span style={{ display: "inline-flex", alignItems: "center" }}>
                    {icon}
                    <ScreenReaderLabel>{label}</ScreenReaderLabel>
                </span>
            </Tooltip>
        )
    } else if (help) {
        return (
            <Tooltip slotProps={{ tooltip: { sx: { maxWidth: "30em" } } }} title={help}>
                <span>{label}</span>
            </Tooltip>
        )
    } else if (icon) {
        return icon
    } else {
        return label
    }
}
TableHeaderCellContents.propTypes = {
    help: popupContentPropType,
    label: labelPropType,
    icon: PropTypes.node,
}

const ScreenReaderLabel = ({ children }) => (
    <span
        style={{
            position: "absolute",
            width: 1,
            height: 1,
            padding: 0,
            overflow: "hidden",
            clip: "rect(0,0,0,0)",
            whiteSpace: "nowrap",
            border: 0,
        }}
    >
        {children}
    </span>
)
ScreenReaderLabel.propTypes = {
    children: PropTypes.node,
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

export function UnsortableTableHeaderCell({ colSpan, help, label, textAlign, width, icon }) {
    return (
        <TableCell align={textAlign} colSpan={colSpan} width={width} aria-label={label}>
            <TableHeaderCellContents help={help} label={label} icon={icon} />
        </TableCell>
    )
}
UnsortableTableHeaderCell.propTypes = {
    colSpan: string,
    help: popupContentPropType,
    label: labelPropType,
    textAlign: string,
    width: string,
    icon: PropTypes.node,
}
