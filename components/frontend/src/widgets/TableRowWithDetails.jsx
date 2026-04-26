import { Stack, TableCell, TableRow } from "@mui/material"
import { bool, func, node, object, string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"
import { ExpandButton } from "./buttons/ExpandButton"

export function TableRowWithDetails(props) {
    const { color, firstCellContent, firstCellProps, children, details, expanded, onExpand, ...otherProps } = props
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
                    "& > *": { borderBottom: expanded ? "unset" : "set" },
                }}
            >
                <TableCell {...firstCellProps}>
                    <Stack direction="row" sx={{ alignItems: "center", paddingLeft: "8px", height: "100%" }}>
                        <ExpandButton
                            expand={expanded}
                            onClick={(event) => {
                                event.stopPropagation()
                                onExpand(!expanded)
                            }}
                        />
                        {firstCellContent}
                    </Stack>
                </TableCell>
                {children}
            </TableRow>
            {expanded && (
                <TableRow>
                    <TableCell colSpan="99" sx={{ paddingLeft: "50px" }}>
                        {details}
                    </TableCell>
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
    firstCellContent: node,
    firstCellProps: object,
    onExpand: func,
}
