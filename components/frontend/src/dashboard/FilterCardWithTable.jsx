import { Chip, Table, TableBody, TableCell, TableRow } from "@mui/material"
import { bool, func, string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"
import { DashboardCard } from "./DashboardCard"

export function FilterCardWithTable({ children, onClick, selected, title }) {
    return (
        <DashboardCard onClick={onClick} selected={selected} title={title} titleFirst={true}>
            <Table size="small">
                <TableBody>{children}</TableBody>
            </Table>
        </DashboardCard>
    )
}
FilterCardWithTable.propTypes = {
    children: childrenPropType,
    onClick: func,
    selected: bool,
    title: string,
}

function Row({ color, label, value }) {
    return (
        <TableRow>
            <TableCell
                sx={{
                    fontSize: "12px",
                    paddingLeft: "0px",
                    whiteSpace: "nowrap",
                    width: "100%",
                    maxWidth: 0,
                    overflow: "hidden",
                }}
            >
                {label}
            </TableCell>
            <TableCell sx={{ paddingRight: "0px", textAlign: "right" }}>
                <Chip color={color} label={value} size="small" sx={{ borderRadius: 1 }} />
            </TableCell>
        </TableRow>
    )
}
Row.propTypes = {
    color: string,
    label: string,
    value: string,
}

FilterCardWithTable.Row = Row
