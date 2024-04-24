import "./IssuesCard.css"

import { bool, func } from "prop-types"

import { Card, Header, Label, Table } from "../semantic_ui_react_wrappers"
import { reportPropType } from "../sharedPropTypes"
import { capitalize, ISSUE_STATUS_COLORS } from "../utils"

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
    const tableRows = Object.keys(statuses).map((status) => (
        <Table.Row key={status}>
            <Table.Cell>{capitalize(status)}</Table.Cell>
            <Table.Cell textAlign="right">
                <Label size="small" color={ISSUE_STATUS_COLORS[status]}>
                    {statuses[status]}
                </Label>
            </Table.Cell>
        </Table.Row>
    ))
    const color = selected ? "blue" : null
    return (
        <Card className="issues" color={color} onClick={onClick} onKeyPress={onClick} tabIndex="0">
            <Card.Content>
                <Header as="h3" color={color} textAlign="center">
                    {"Issues"}
                </Header>
                <Table basic="very" compact="very" size="small">
                    <Table.Body>{tableRows}</Table.Body>
                </Table>
            </Card.Content>
        </Card>
    )
}
IssuesCard.propTypes = {
    onClick: func,
    report: reportPropType,
    selected: bool,
}
