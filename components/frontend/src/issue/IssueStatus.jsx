import { Card, CardActionArea, CardContent, List, ListItem, Tooltip, Typography } from "@mui/material"
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { bool, string } from "prop-types"

import { issueStatusPropType, metricPropType, settingsPropType, stringsPropType } from "../sharedPropTypes"
import { getMetricIssueIds } from "../utils"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

dayjs.extend(relativeTime)

function IssueWithoutTracker({ issueId }) {
    return (
        <Tooltip
            title={
                <>
                    <h4>No issue tracker configured</h4>
                    <p>
                        Please configure an issue tracker by expanding the report title, selecting the &lsquo;Issue
                        tracker&rsquo; tab, and configuring an issue tracker.
                    </p>
                </>
            }
        >
            <span>
                <Card elevation={1} sx={{ display: "inline-flex", margin: "1px" }}>
                    <CardActionArea disableRipple>
                        <CardContent sx={{ padding: "8px" }}>
                            <Typography color="error" noWrap>
                                {issueId} - ?
                            </Typography>
                        </CardContent>
                    </CardActionArea>
                </Card>
            </span>
        </Tooltip>
    )
}
IssueWithoutTracker.propTypes = {
    issueId: string,
}

function IssuesWithoutTracker({ issueIds }) {
    return (
        <>
            {issueIds.map((issueId) => (
                <IssueWithoutTracker key={issueId} issueId={issueId} />
            ))}
        </>
    )
}
IssuesWithoutTracker.propTypes = {
    issueIds: stringsPropType,
}

function cardDetails(issueStatus, settings) {
    let details = []
    if (issueStatus.summary && settings.showIssueSummary.value) {
        details.push(<ListItem key="summary">{issueStatus.summary}</ListItem>)
    }
    if (issueStatus.created && settings.showIssueCreationDate.value) {
        details.push(
            <ListItem key="created">
                <Typography noWrap variant="inherit">
                    Created {dayjs(issueStatus.created).fromNow()}
                </Typography>
            </ListItem>,
        )
    }
    if (issueStatus.updated && settings.showIssueUpdateDate.value) {
        details.push(
            <ListItem key="updated">
                <Typography noWrap variant="inherit">
                    Updated {dayjs(issueStatus.updated).fromNow()}
                </Typography>
            </ListItem>,
        )
    }
    if (issueStatus.duedate && settings.showIssueDueDate.value) {
        details.push(
            <ListItem key="duedate">
                <Typography noWrap variant="inherit">
                    Due {dayjs(issueStatus.duedate).fromNow()}
                </Typography>
            </ListItem>,
        )
    }
    if (issueStatus.release_name && settings.showIssueRelease.value) {
        details.push(release(issueStatus))
    }
    if (issueStatus.sprint_name && settings.showIssueSprint.value) {
        details.push(sprint(issueStatus))
    }
    return details.length > 0 ? <List dense>{details}</List> : null
}
cardDetails.propTypes = {
    issueStatus: issueStatusPropType,
    settings: settingsPropType,
}

function releaseStatus(issueStatus) {
    return issueStatus.release_released ? "released" : "planned"
}
releaseStatus.propTypes = {
    issueStatus: issueStatusPropType,
}

function release(issueStatus) {
    const date = issueStatus.release_date ? dayjs(issueStatus.release_date).fromNow() : null
    return (
        <ListItem key="release">
            {prefixName(issueStatus.release_name, "Release")} {releaseStatus(issueStatus)} {date}
        </ListItem>
    )
}
release.propTypes = {
    issueStatus: issueStatusPropType,
}

function sprint(issueStatus) {
    const sprintEnd = issueStatus.sprint_enddate ? <>ends {dayjs(issueStatus.sprint_enddate).fromNow()}</> : null
    return (
        <ListItem key="sprint">
            {prefixName(issueStatus.sprint_name, "Sprint")} ({issueStatus.sprint_state}) {sprintEnd}
        </ListItem>
    )
}
sprint.propTypes = {
    issueStatus: issueStatusPropType,
}

function prefixName(name, prefix) {
    // Prefix the name with prefix unless the name already contains the prefix
    return name.toLowerCase().includes(prefix.toLowerCase()) ? name : `${prefix} ${name}`
}
prefixName.propType = {
    name: string,
    prefix: string,
}

function IssueCard({ issueStatus, settings, error }) {
    // The issue status can be unknown when the issue was added recently and the status hasn't been collected yet
    const color = error ? "error" : (issueStatus.status_category ?? "unknown")
    const onClick = issueStatus.landing_url ? () => globalThis.open(issueStatus.landing_url) : null
    return (
        <Card onClick={onClick} elevation={1} sx={{ display: "inline-flex", margin: "1px" }}>
            <CardActionArea disableRipple={!issueStatus.landing_url}>
                <CardContent sx={{ padding: "8px" }}>
                    <Typography color={color} noWrap>
                        {issueStatus.issue_id} - {issueStatus.name || "?"}
                    </Typography>
                    <Typography
                        component="span" // Default component is p. Use span to prevent "Warning: validateDOMNesting(...): <ul> cannot appear as a descendant of <p>."
                        variant="body2"
                    >
                        {cardDetails(issueStatus, settings)}
                    </Typography>
                </CardContent>
            </CardActionArea>
        </Card>
    )
}
IssueCard.propTypes = {
    issueStatus: issueStatusPropType,
    settings: settingsPropType,
    error: string,
}

function IssueWithTracker({ issueStatus, settings }) {
    let popupContent = "" // Will contain error if any, otherwise creation and update dates, if any, else be empty
    let popupHeader = ""
    if (issueStatus.connection_error) {
        popupHeader = "Connection error"
        popupContent = "Quality-time could not retrieve data from the issue tracker."
    }
    if (issueStatus.parse_error) {
        popupHeader = "Parse error"
        popupContent = "Quality-time could not parse the data received from the issue tracker."
    }
    let card = <IssueCard error={popupHeader} issueStatus={issueStatus} settings={settings} />
    if (!popupContent && issueStatus.created) {
        popupHeader = issueStatus.summary
        popupContent = issuePopupContent(issueStatus)
    }
    if (popupContent) {
        card = (
            <Tooltip
                title={
                    <>
                        <h4>{popupHeader}</h4>
                        {popupContent}
                    </>
                }
            >
                <span>{card}</span>
            </Tooltip>
        )
    }
    return card
}
IssueWithTracker.propTypes = {
    issueStatus: issueStatusPropType,
    settings: settingsPropType,
}

function issuePopupContent(issueStatus) {
    let popupContent = <TimeAgoWithDate date={issueStatus.created}>Created</TimeAgoWithDate>
    if (issueStatus.updated) {
        popupContent = (
            <>
                {popupContent}
                <br />
                <TimeAgoWithDate date={issueStatus.updated}>Updated</TimeAgoWithDate>
            </>
        )
    }
    if (issueStatus.duedate) {
        popupContent = (
            <>
                {popupContent}
                <br />
                <TimeAgoWithDate date={issueStatus.duedate}>Due</TimeAgoWithDate>
            </>
        )
    }
    if (issueStatus.release_name) {
        const releaseDate = issueStatus.release_date ? (
            <TimeAgoWithDate date={issueStatus.release_date}>{releaseStatus(issueStatus)}</TimeAgoWithDate>
        ) : null
        popupContent = (
            <>
                {popupContent}
                <br />
                {prefixName(issueStatus.release_name, "Release")} {releaseDate}
            </>
        )
    }
    if (issueStatus.sprint_name) {
        const sprintEnd = issueStatus.sprint_enddate ? (
            <TimeAgoWithDate date={issueStatus.sprint_enddate}>ends</TimeAgoWithDate>
        ) : null
        popupContent = (
            <>
                {popupContent}
                <br />
                {prefixName(issueStatus.sprint_name, "Sprint")} ({issueStatus.sprint_state}) {sprintEnd}
            </>
        )
    }
    return popupContent
}
issuePopupContent.propTypes = {
    issueStatus: issueStatusPropType,
}

function IssuesWithTracker({ issueIds, metric, settings }) {
    const issueStatuses = metric.issue_status || []
    return (
        <>
            {issueStatuses
                .filter((issueStatus) => issueIds.includes(issueStatus.issue_id))
                .map((issueStatus) => (
                    <IssueWithTracker key={issueStatus.issue_id} issueStatus={issueStatus} settings={settings} />
                ))}
        </>
    )
}
IssuesWithTracker.propTypes = {
    issueIds: stringsPropType,
    metric: metricPropType,
    settings: settingsPropType,
}

export function IssueStatus({ metric, issueTrackerMissing, settings }) {
    const issueIds = getMetricIssueIds(metric)
    if (issueTrackerMissing && issueIds.length > 0) {
        return <IssuesWithoutTracker issueIds={issueIds} />
    }
    return <IssuesWithTracker issueIds={issueIds} metric={metric} settings={settings} />
}
IssueStatus.propTypes = {
    issueTrackerMissing: bool,
    metric: metricPropType,
    settings: settingsPropType,
}
