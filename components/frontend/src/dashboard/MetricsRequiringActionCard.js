import { bool, func } from "prop-types"

import { STATUS_COLORS, STATUS_NAME, STATUSES_REQUIRING_ACTION } from "../metric/status"
import { Label, Table } from "../semantic_ui_react_wrappers"
import { reportsPropType } from "../sharedPropTypes"
import { getMetricStatus, sum } from "../utils"
import { FilterCardWithTable } from "./FilterCardWithTable"

function metricStatuses(reports) {
    const statuses = {}
    STATUSES_REQUIRING_ACTION.forEach((status) => {
        statuses[status] = 0
    })
    reports.forEach((report) => {
        Object.values(report.subjects).forEach((subject) => {
            Object.values(subject.metrics).forEach((metric) => {
                const status = getMetricStatus(metric)
                if (STATUSES_REQUIRING_ACTION.includes(status)) {
                    statuses[status] += 1
                }
            })
        })
    })
    return statuses
}
metricStatuses.propTypes = {
    reports: reportsPropType,
}

function tableRows(reports) {
    const statuses = metricStatuses(reports)
    const rows = Object.keys(statuses).map((status) => (
        <Table.Row key={status}>
            <Table.Cell>{STATUS_NAME[status]}</Table.Cell>
            <Table.Cell textAlign="right">
                <Label size="small" color={STATUS_COLORS[status] === "white" ? null : STATUS_COLORS[status]}>
                    {statuses[status]}
                </Label>
            </Table.Cell>
        </Table.Row>
    ))
    rows.push(
        <Table.Row key="total">
            <Table.Cell>
                <b>Total</b>
            </Table.Cell>
            <Table.Cell textAlign="right">
                <Label size="small" color="black">
                    {sum(Object.values(statuses))}
                </Label>
            </Table.Cell>
        </Table.Row>,
    )
    return rows
}
tableRows.propTypes = {
    reports: reportsPropType,
}

export function MetricsRequiringActionCard({ onClick, reports, selected }) {
    return (
        <FilterCardWithTable onClick={onClick} selected={selected} title="Action required">
            {tableRows(reports)}
        </FilterCardWithTable>
    )
}
MetricsRequiringActionCard.propTypes = {
    onClick: func,
    reports: reportsPropType,
    selected: bool,
}
