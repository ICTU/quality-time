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

function labelDetails(issueStatus, showIssueCreationDate, showIssueSummary, showIssueUpdateDate, showIssueDueDate) {
    let details = [<Label.Detail key="name">{issueStatus.name || "?"}</Label.Detail>]
    if (issueStatus.summary && showIssueSummary) {
        details.push(<Label.Detail key="summary">{issueStatus.summary}</Label.Detail>)
    }
    if (issueStatus.created && showIssueCreationDate) {
        details.push(<Label.Detail key="created">Created <TimeAgo date={issueStatus.created} /></Label.Detail>)
    }
    if (issueStatus.updated && showIssueUpdateDate) {
        details.push(<Label.Detail key="updated">Updated <TimeAgo date={issueStatus.updated} /></Label.Detail>)
    }
    if (issueStatus.duedate && showIssueDueDate) {
        details.push(<Label.Detail key="duedate">Due <TimeAgo date={issueStatus.duedate} /></Label.Detail>)
    }
    return details
}

function IssueWithTracker({ issueStatus, showIssueCreationDate, showIssueSummary, showIssueUpdateDate, showIssueDueDate }) {
    let popupContent = "";  // Will contain error if any, otherwise creation and update dates, if any, else be empty
    let popupHeader = "";
    if (issueStatus.connection_error) { popupHeader = "Connection error"; popupContent = "Quality-time could not retrieve data from the issue tracker." }
    if (issueStatus.parse_error) { popupHeader = "Parse error"; popupContent = "Quality-time could not parse the data received from the issue tracker." }
    const color = popupContent ? "red" : {todo: "grey", doing: "blue", done: "green"}[issueStatus.status_category ?? "todo"];
    const basic = popupContent ? false : true;
    let label = <Label basic={basic} color={color}>{issueStatus.issue_id}{labelDetails(issueStatus, showIssueCreationDate, showIssueSummary, showIssueUpdateDate, showIssueDueDate)}</Label>
    if (issueStatus.landing_url) {
        // Without the span, the popup doesn't work
        label = <span><HyperLink url={issueStatus.landing_url}>{label}</HyperLink></span>
    }
    if (!popupContent && issueStatus.created) {
        popupHeader = issueStatus.summary;
        popupContent = <TimeAgoWithDate date={issueStatus.created}>Created</TimeAgoWithDate>
        if (issueStatus.updated) {
            popupContent = <>{popupContent}<br /><TimeAgoWithDate date={issueStatus.updated}>Updated</TimeAgoWithDate></>
        }
        if (issueStatus.duedate) {
            popupContent = <>{popupContent}<br /><TimeAgoWithDate date={issueStatus.duedate}>Due</TimeAgoWithDate></>
        }
    }
    if (popupContent) {
        label = <Popup header={popupHeader} content={popupContent} flowing hoverable trigger={label} />
    }
    return label
}

function IssuesWithTracker({ metric, showIssueCreationDate, showIssueSummary, showIssueUpdateDate, showIssueDueDate }) {
    const issueStatuses = metric.issue_status || [];
    return <>{issueStatuses.map((issueStatus) => <IssueWithTracker
        key={issueStatus.issue_id}
        issueStatus={issueStatus}
        showIssueCreationDate={showIssueCreationDate}
        showIssueSummary={showIssueSummary}
        showIssueUpdateDate={showIssueUpdateDate}
        showIssueDueDate={showIssueDueDate}
    />)}</>
}

export function IssueStatus({ metric, issueTrackerMissing, showIssueCreationDate, showIssueSummary, showIssueUpdateDate, showIssueDueDate }) {
    if (issueTrackerMissing && metric.issue_ids?.length > 0) {
        return <IssuesWithoutTracker issueIds={metric.issue_ids} />
    }
    return <IssuesWithTracker
        metric={metric}
        showIssueCreationDate={showIssueCreationDate}
        showIssueSummary={showIssueSummary}
        showIssueUpdateDate={showIssueUpdateDate}
        showIssueDueDate={showIssueDueDate}
    />
}
