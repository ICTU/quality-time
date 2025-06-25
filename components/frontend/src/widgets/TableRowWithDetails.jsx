import { Stack, TableCell, TableRow } from "@mui/material"
import { bool, func, string } from "prop-types"
import React from "react"

import { childrenPropType } from "../sharedPropTypes"
import { ExpandButton } from "./buttons/ExpandButton"

export function TableRowWithDetails(props) {
    const { color, children, details, expanded, onExpand, ...otherProps } = props
    const [firstTableCell, ...otherTableCells] = React.Children.toArray(children)
    const firstTableCellWithExpandButton = React.cloneElement(
        firstTableCell,
        null,
        <Stack direction="row" alignItems="center">
            <ExpandButton expand={expanded} onClick={() => onExpand(!expanded)} /> {firstTableCell.props.children}
        </Stack>,
    )
    return (
        <>
            <TableRow
                {...otherProps}
                hover
                sx={{
                    bgcolor: `${color}.bgcolor`,
                    "&.MuiTableRow-hover": {
                        "&:hover": {
                            backgroundColor: `${color}.hover`,
                        },
                    },
                }}
            >
                {firstTableCellWithExpandButton}
                {otherTableCells}
            </TableRow>
            {expanded && (
                <TableRow>
                    <TableCell colSpan="99">{details}</TableCell>
                </TableRow>
            )}
        </>
    )
}
TableRowWithDetails.propTypes = {
    children: childrenPropType,
    color: string,
    details: childrenPropType,
    expanded: bool,
    onExpand: func,
}
