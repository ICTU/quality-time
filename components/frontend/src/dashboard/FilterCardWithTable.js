import { Table, TableBody } from "@mui/material"
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
