import React from 'react';
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { HyperLink } from '../widgets/HyperLink';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import TimeAgo from 'react-timeago';

function IssueWithoutTracker({ issueId }) {
    return (
        <Popup
            content={"Please configure an issue tracker by expanding the report title, selecting the 'Issue tracker' tab, and configuring an issue tracker."}
            header={"No issue tracker configured"}
            trigger={<Label color="red">{issueId}</Label>}
        />
    )
}

function IssuesWithoutTracker({ issueIds }) {
    return <>{issueIds.map((issueId) => <IssueWithoutTracker key={issueId} issueId={issueId} />)}</>
}

function labelDetails(issueStatus, issueSettings) {
    let details = [<Label.Detail key="name">{issueStatus.name || "?"}</Label.Detail>]
    if (issueStatus.summary && issueSettings?.showIssueSummary) {
        details.push(<Label.Detail key="summary">{issueStatus.summary}</Label.Detail>)
    }
    if (issueStatus.created && issueSettings?.showIssueCreationDate) {
        details.push(<Label.Detail key="created">Created <TimeAgo date={issueStatus.created} /></Label.Detail>)
    }
    if (issueStatus.updated && issueSettings?.showIssueUpdateDate) {
        details.push(<Label.Detail key="updated">Updated <TimeAgo date={issueStatus.updated} /></Label.Detail>)
    }
    if (issueStatus.duedate && issueSettings?.showIssueDueDate) {
        details.push(<Label.Detail key="duedate">Due <TimeAgo date={issueStatus.duedate} /></Label.Detail>)
    }
    if (issueStatus.release_name && issueSettings?.showIssueRelease) {
        details.push(releaseLabel(issueStatus))
    }
    if (issueStatus.sprint_name && issueSettings?.showIssueSprint) {
        details.push(sprintLabel(issueStatus))
    }
    return details
}

function releaseLabel(issueStatus) {
    const date = issueStatus.release_date ? <TimeAgo date={issueStatus.release_date}/> : null
    return (
        <Label.Detail key="release">
            {prefixName(issueStatus.release_name, "Release")} {issueStatus.release_released ? "released" : "planned"} {date}
        </Label.Detail>
    )
}

function sprintLabel(issueStatus) {
    const sprintEnd = issueStatus.sprint_enddate ? <>ends <TimeAgo date={issueStatus.sprint_enddate}/></> : null
    return (
        <Label.Detail key="sprint">
            {prefixName(issueStatus.sprint_name, "Sprint")} ({issueStatus.sprint_state}) {sprintEnd}
        </Label.Detail>
    )
}

function prefixName(name, prefix) {
    return name.toLowerCase().indexOf(name.toLowerCase()) < 0 ? `${prefix} ${name}` : name;
}

function issueLabel(issueStatus, issueSettings, error) {
    const color = error ? "red" : {todo: "grey", doing: "blue", done: "green"}[issueStatus.status_category ?? "todo"];
    const label = <Label basic={!error} color={color}>{issueStatus.issue_id}{labelDetails(issueStatus, issueSettings)}</Label>
    if (issueStatus.landing_url) {
        // Without the span, the popup doesn't work
        return <span><HyperLink url={issueStatus.landing_url}>{label}</HyperLink></span>
    }
    return label
}

function IssueWithTracker({ issueStatus, issueSettings }) {
    let popupContent = "";  // Will contain error if any, otherwise creation and update dates, if any, else be empty
    let popupHeader = "";
    if (issueStatus.connection_error) {
        popupHeader = "Connection error";
        popupContent = "Quality-time could not retrieve data from the issue tracker."
    }
    if (issueStatus.parse_error) {
        popupHeader = "Parse error";
        popupContent = "Quality-time could not parse the data received from the issue tracker."
    }
    let label = issueLabel(issueStatus, issueSettings, popupHeader)
    if (!popupContent && issueStatus.created) {
        popupHeader = issueStatus.summary;
        popupContent = <TimeAgoWithDate date={issueStatus.created}>Created</TimeAgoWithDate>
        if (issueStatus.updated) {
            popupContent = <>{popupContent}<br /><TimeAgoWithDate date={issueStatus.updated}>Updated</TimeAgoWithDate></>
        }
        if (issueStatus.duedate) {
            popupContent = <>{popupContent}<br /><TimeAgoWithDate date={issueStatus.duedate}>Due</TimeAgoWithDate></>
        }
        if (issueStatus.release_name) {
            const releaseStatus = issueStatus.release_released ? "released" : "planned";
            const releaseDate = issueStatus.release_date ? <TimeAgoWithDate date={issueStatus.release_date}>{releaseStatus}</TimeAgoWithDate> : null
            popupContent = <>{popupContent}<br />{prefixName(issueStatus.release_name, "Release")} {releaseDate}</>
        }
        if (issueStatus.sprint_name) {
            const sprintEnd = issueStatus.sprint_enddate ? <TimeAgoWithDate date={issueStatus.sprint_enddate}>ends</TimeAgoWithDate> : null
            popupContent = <>{popupContent}<br />{prefixName(issueStatus.sprint_name, "Sprint")} ({issueStatus.sprint_state}) {sprintEnd}</>
        }
    }
    if (popupContent) {
        label = <Popup header={popupHeader} content={popupContent} flowing hoverable trigger={label} />
    }
    return label
}

function IssuesWithTracker({ metric, issueSettings }) {
    const issueStatuses = metric.issue_status || [];
    return <>{issueStatuses.map((issueStatus) => <IssueWithTracker
        key={issueStatus.issue_id}
        issueStatus={issueStatus}
        issueSettings={issueSettings}
    />)}</>
}

export function IssueStatus({ metric, issueTrackerMissing, issueSettings }) {
    if (issueTrackerMissing && metric.issue_ids?.length > 0) {
        return <IssuesWithoutTracker issueIds={metric.issue_ids} />
    }
    return <IssuesWithTracker metric={metric} issueSettings={issueSettings} />
}
