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

export function MetricsRequiringActionCard({ onClick, reports, selected }) {
    const statuses = metricStatuses(reports)
    const total = sum(Object.values(statuses))
    return (
        <FilterCardWithTable onClick={onClick} selected={selected} title="Action required" total={total}>
            {Object.entries(statuses).map(([status, count]) => (
                <FilterCardWithTable.Row key={status} color={status} label={STATUS_NAME[status]} value={count} />
            ))}
        </FilterCardWithTable>
    )
}
MetricsRequiringActionCard.propTypes = {
    onClick: func,
    reports: reportsPropType,
    selected: bool,
}
