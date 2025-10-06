import { Chip, Table, TableBody, TableCell, TableRow } from "@mui/material"
import { bool, func, number, string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"
import { DashboardCard } from "./DashboardCard"

export function FilterCardWithTable({ children, onClick, selected, title, total }) {
    return (
        <DashboardCard onClick={onClick} selected={selected} title={title} titleFirst={true}>
            <Table size="small" padding="none" height="75%">
                <TableBody>
                    {children}
                    <Row key="total" color="total" label={<b>Total</b>} value={total} />
                </TableBody>
            </Table>
        </DashboardCard>
    )
}
FilterCardWithTable.propTypes = {
    children: childrenPropType,
    onClick: func,
    selected: bool,
    title: string,
    total: number,
}

function Row({ color, label, value }) {
    return (
        <TableRow
            sx={{
                "&:last-child th, &:last-child td": {
                    borderBottom: 0,
                },
            }}
        >
            <TableCell
                sx={{
                    fontSize: "1.3em",
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
