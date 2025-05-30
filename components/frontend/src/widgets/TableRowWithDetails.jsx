import { TableCell, TableRow } from "@mui/material"
import { bool, func, string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"
import { ExpandButton } from "./buttons/ExpandButton"

export function TableRowWithDetails(props) {
    const { color, children, details, expanded, onExpand, ...otherProps } = props
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
                <TableCell align="center" padding="checkbox" /* Make sure the column does not stretch */>
                    <ExpandButton expand={expanded} onClick={() => onExpand(!expanded)} />
                </TableCell>
                {children}
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
