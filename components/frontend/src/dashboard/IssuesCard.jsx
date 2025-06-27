import { bool, func } from "prop-types"

import { reportPropType } from "../sharedPropTypes"
import { capitalize } from "../utils"
import { FilterCardWithTable } from "./FilterCardWithTable"

function issueStatuses(report) {
    // The issue status is unknown when the issue was added recently and the status hasn't been collected yet
    // or when collecting the issue status from the issue tracker failed
    const statuses = { todo: 0, doing: 0, done: 0, unknown: 0 }
    Object.values(report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
            let nrIssuesWithKnownStatus = 0
            const issueStatus = metric.issue_status ?? []
            issueStatus.forEach((issue) => {
                if (issue.status_category) {
                    statuses[issue.status_category] += 1
                    nrIssuesWithKnownStatus += 1
                }
            })
            const nrIssues = metric.issue_ids?.length ?? 0
            statuses["unknown"] += nrIssues - nrIssuesWithKnownStatus
        })
    })
    return statuses
}
issueStatuses.propTypes = {
    report: reportPropType,
}

export function IssuesCard({ onClick, report, selected }) {
    const statuses = issueStatuses(report)
    return (
        <FilterCardWithTable onClick={onClick} selected={selected} title="Issues">
            {Object.entries(statuses).map(([status, count]) => (
                <FilterCardWithTable.Row key={status} color={status} label={capitalize(status)} value={count} />
            ))}
        </FilterCardWithTable>
    )
}
IssuesCard.propTypes = {
    onClick: func,
    report: reportPropType,
    selected: bool,
}
