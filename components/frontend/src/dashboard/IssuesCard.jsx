import { bool, func } from "prop-types"

import { reportPropType } from "../sharedPropTypes"
import { capitalize, sum } from "../utils"
import { FilterCardWithTable } from "./FilterCardWithTable"

function issueStatuses(report) {
    // The issue status is unknown when the issue was added recently and the status hasn't been collected yet
    // or when collecting the issue status from the issue tracker failed
    const statuses = { unknown: 0, todo: 0, doing: 0, done: 0 }
    for (const subject of Object.values(report.subjects)) {
        for (const metric of Object.values(subject.metrics)) {
            let nrIssuesWithKnownStatus = 0
            const issueStatus = metric.issue_status ?? []
            for (const issue of issueStatus) {
                if (issue.status_category) {
                    statuses[issue.status_category] += 1
                    nrIssuesWithKnownStatus += 1
                }
            }
            const nrIssues = metric.issue_ids?.length ?? 0
            statuses["unknown"] += nrIssues - nrIssuesWithKnownStatus
        }
    }
    return statuses
}
issueStatuses.propTypes = {
    report: reportPropType,
}

export function IssuesCard({ onClick, report, selected }) {
    const statuses = issueStatuses(report)
    const total = sum(Object.values(statuses))
    return (
        <FilterCardWithTable onClick={onClick} selected={selected} title="Issues" total={total}>
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
