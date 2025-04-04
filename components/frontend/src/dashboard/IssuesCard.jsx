import { Chip, TableCell, TableRow } from "@mui/material"
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

function tableRows(report) {
    const statuses = issueStatuses(report)
    return Object.keys(statuses).map((status) => (
        <TableRow key={status}>
            <TableCell sx={{ fontSize: "12px", paddingLeft: "0px" }}>{capitalize(status)}</TableCell>
            <TableCell sx={{ paddingRight: "0px", textAlign: "right" }}>
                <Chip color={status} label={`${statuses[status]}`} size="small" sx={{ borderRadius: 1 }} />
            </TableCell>
        </TableRow>
    ))
}
tableRows.propTypes = {
    report: reportPropType,
}

export function IssuesCard({ onClick, report, selected }) {
    return (
        <FilterCardWithTable onClick={onClick} selected={selected} title="Issues">
            {tableRows(report)}
        </FilterCardWithTable>
    )
}
IssuesCard.propTypes = {
    onClick: func,
    report: reportPropType,
    selected: bool,
}
