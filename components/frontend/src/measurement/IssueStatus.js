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

function labelDetails(issueStatus, issueTracker) {
    let details = [<Label.Detail key="name">{issueStatus.name || "?"}</Label.Detail>]
    if (issueStatus.summary && issueTracker?.parameters?.show_issue_summary) {
        details.push(<Label.Detail key="summary">{issueStatus.summary}</Label.Detail>)
    }
    if (issueStatus.created && issueTracker?.parameters?.show_issue_creation_date) {
        details.push(<Label.Detail key="created">Created <TimeAgo date={issueStatus.created} /></Label.Detail>)
    }
    if (issueStatus.updated && issueTracker?.parameters?.show_issue_update_date) {
        details.push(<Label.Detail key="updated">Updated <TimeAgo date={issueStatus.updated} /></Label.Detail>)
    }
    return details
}

function IssueWithTracker({ issueStatus, issueTracker }) {
    let popupContent = "";  // Will contain error if any, otherwise creation and update dates, if any, else be empty
    if (issueStatus.connection_error) { popupContent = "Connection error" }
    if (issueStatus.parse_error) { popupContent = "Parse error" }
    const color = popupContent ? "red" : "blue";
    const basic = popupContent ? false : true;
    let label = <Label basic={basic} color={color}>{issueStatus.issue_id}{labelDetails(issueStatus, issueTracker)}</Label>
    if (issueStatus.landing_url) {
        // Without the span, the popup doesn't work
        label = <span><HyperLink url={issueStatus.landing_url}>{label}</HyperLink></span>
    }
    if (!popupContent && issueStatus.created) {
        popupContent = <TimeAgoWithDate date={issueStatus.created}>Created</TimeAgoWithDate>
        if (issueStatus.updated) {
            popupContent = <>{popupContent}<br /><TimeAgoWithDate date={issueStatus.updated}>Updated</TimeAgoWithDate></>
        }
    }
    if (popupContent) {
        label = <Popup header={issueStatus.summary} content={popupContent} flowing hoverable trigger={label} />
    }
    return label
}

function IssuesWithTracker({ metric, issueTracker }) {
    const issueStatuses = metric.issue_status || [];
    return <>{issueStatuses.map((issueStatus) => <IssueWithTracker key={issueStatus.issue_id} issueStatus={issueStatus} issueTracker={issueTracker} />)}</>
}

export function IssueStatus({ metric, issueTracker }) {
    if (!issueTracker && metric.issue_ids?.length > 0) {
        return <IssuesWithoutTracker issueIds={metric.issue_ids} />
    }
    return <IssuesWithTracker metric={metric} issueTracker={issueTracker} />
}
