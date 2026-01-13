import { bool, func } from "prop-types"

import { reportPropType } from "../sharedPropTypes"
import { capitalize, sum } from "../utils"
import { FilterCardWithTable } from "./FilterCardWithTable"

function issueStatuses(report) {
    // The issue status is unknown when the issue was added recently and the status hasn't been collected yet
    // or when collecting the issue status from the issue tracker failed
    const statuses = { unknown: 0, todo: 0, doing: 0, done: 0 }
    const issueIds = new Set()
    for (const subject of Object.values(report.subjects)) {
        for (const metric of Object.values(subject.metrics)) {
            for (const issueId of metric.issue_ids ?? []) {
                if (issueIds.has(issueId)) {
                    continue // Count issues linked to multiple metrics only once
                }
                issueIds.add(issueId)
                // Find the status for the issue id and count it. Count as unknown if the status can't be found.
                const issueStatus = (metric.issue_status ?? []).find((issueStatus) => issueStatus.issue_id === issueId)
                statuses[issueStatus?.status_category ?? "unknown"] += 1
            }
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
