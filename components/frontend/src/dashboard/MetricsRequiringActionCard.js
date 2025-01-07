import { Chip, TableCell, TableRow } from "@mui/material"
import { bool, func } from "prop-types"

import { STATUS_NAME, STATUSES_REQUIRING_ACTION } from "../metric/status"
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
        <TableRow key={status}>
            <TableCell sx={{ fontSize: "12px", paddingLeft: "0px" }}>{STATUS_NAME[status]}</TableCell>
            <TableCell sx={{ paddingRight: "0px", textAlign: "right" }}>
                <Chip color={status} label={statuses[status]} size="small" sx={{ borderRadius: 1 }} />
            </TableCell>
        </TableRow>
    ))
    rows.push(
        <TableRow key="total">
            <TableCell sx={{ fontSize: "12px", paddingLeft: "0px" }}>
                <b>Total</b>
            </TableCell>
            <TableCell sx={{ paddingRight: "0px", textAlign: "right" }}>
                <Chip color="total" label={sum(Object.values(statuses))} size="small" sx={{ borderRadius: 1 }} />
            </TableCell>
        </TableRow>,
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
