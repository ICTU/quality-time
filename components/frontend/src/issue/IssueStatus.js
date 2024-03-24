import { bool, string } from "prop-types"
import TimeAgo from "react-timeago"

import { Label, Popup } from "../semantic_ui_react_wrappers"
import { issueStatusPropType, metricPropType, settingsPropType, stringsPropType } from "../sharedPropTypes"
import { getMetricIssueIds } from "../utils"
import { HyperLink } from "../widgets/HyperLink"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

function IssueWithoutTracker({ issueId }) {
    return (
        <Popup
            content={
                "Please configure an issue tracker by expanding the report title, selecting the 'Issue tracker' tab, and configuring an issue tracker."
            }
            header={"No issue tracker configured"}
            trigger={<Label color="red">{issueId}</Label>}
        />
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

function labelDetails(issueStatus, settings) {
    let details = [<Label.Detail key="name">{issueStatus.name || "?"}</Label.Detail>]
    if (issueStatus.summary && settings.showIssueSummary.value) {
        details.push(<Label.Detail key="summary">{issueStatus.summary}</Label.Detail>)
    }
    if (issueStatus.created && settings.showIssueCreationDate.value) {
        details.push(
            <Label.Detail key="created">
                Created <TimeAgo date={issueStatus.created} />
            </Label.Detail>,
        )
    }
    if (issueStatus.updated && settings.showIssueUpdateDate.value) {
        details.push(
            <Label.Detail key="updated">
                Updated <TimeAgo date={issueStatus.updated} />
            </Label.Detail>,
        )
    }
    if (issueStatus.duedate && settings.showIssueDueDate.value) {
        details.push(
            <Label.Detail key="duedate">
                Due <TimeAgo date={issueStatus.duedate} />
            </Label.Detail>,
        )
    }
    if (issueStatus.release_name && settings.showIssueRelease.value) {
        details.push(releaseLabel(issueStatus))
    }
    if (issueStatus.sprint_name && settings.showIssueSprint.value) {
        details.push(sprintLabel(issueStatus))
    }
    return details
}
labelDetails.propTypes = {
    issueStatus: issueStatusPropType,
    settings: settingsPropType,
}

function releaseStatus(issueStatus) {
    return issueStatus.release_released ? "released" : "planned"
}
releaseStatus.propTypes = {
    issueStatus: issueStatusPropType,
}

function releaseLabel(issueStatus) {
    const date = issueStatus.release_date ? <TimeAgo date={issueStatus.release_date} /> : null
    return (
        <Label.Detail key="release">
            {prefixName(issueStatus.release_name, "Release")} {releaseStatus(issueStatus)} {date}
        </Label.Detail>
    )
}
releaseLabel.propTypes = {
    issueStatus: issueStatusPropType,
}

function sprintLabel(issueStatus) {
    const sprintEnd = issueStatus.sprint_enddate ? (
        <>
            ends <TimeAgo date={issueStatus.sprint_enddate} />
        </>
    ) : null
    return (
        <Label.Detail key="sprint">
            {prefixName(issueStatus.sprint_name, "Sprint")} ({issueStatus.sprint_state}) {sprintEnd}
        </Label.Detail>
    )
}
sprintLabel.propTypes = {
    issueStatus: issueStatusPropType,
}

function prefixName(name, prefix) {
    // Prefix the name with prefix unless the name already contains the prefix
    return name.toLowerCase().indexOf(prefix.toLowerCase()) < 0 ? `${prefix} ${name}` : name
}
prefixName.propType = {
    name: string,
    prefix: string,
}

function issueLabel(issueStatus, settings, error) {
    const color = error ? "red" : { todo: "grey", doing: "blue", done: "green" }[issueStatus.status_category ?? "todo"]
    const label = (
        <Label basic={!error} color={color}>
            {issueStatus.issue_id}
            {labelDetails(issueStatus, settings)}
        </Label>
    )
    if (issueStatus.landing_url) {
        // Without the span, the popup doesn't work
        return (
            <span>
                <HyperLink url={issueStatus.landing_url}>{label}</HyperLink>
            </span>
        )
    }
    return label
}
issueLabel.propTypes = {
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
    let label = issueLabel(issueStatus, settings, popupHeader)
    if (!popupContent && issueStatus.created) {
        popupHeader = issueStatus.summary
        popupContent = issuePopupContent(issueStatus)
    }
    if (popupContent) {
        label = <Popup header={popupHeader} content={popupContent} flowing hoverable trigger={label} />
    }
    return label
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
                .filter((issueStatus) => issueIds.indexOf(issueStatus.issue_id) > -1)
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
