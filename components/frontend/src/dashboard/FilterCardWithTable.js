import { bool, func, string } from "prop-types"

import { Table } from "../semantic_ui_react_wrappers"
import { childrenPropType } from "../sharedPropTypes"
import { DashboardCard } from "./DashboardCard"

export function FilterCardWithTable({ children, onClick, selected, title }) {
    return (
        <DashboardCard onClick={onClick} selected={selected} title={title} titleFirst={true}>
            <Table basic="very" compact="very" size="small">
                <Table.Body>{children}</Table.Body>
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
