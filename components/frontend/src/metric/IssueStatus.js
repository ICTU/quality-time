import React from 'react';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import TimeAgo from 'react-timeago';

export function IssueStatus({ metric, issueTracker }) {
    const issueStatuses = metric.issue_status || [];
    const statuses = issueStatuses.map((issueStatus) => {
        let popupContent = "";  // Will contain error if any, otherwise creation and update dates, if any, else be empty
        if (issueStatus.connection_error) { popupContent = "Connection error" }
        if (issueStatus.parse_error) { popupContent = "Parse error" }
        const color = popupContent ? "red" : "blue";
        const basic = popupContent ? false : true;
        let labelDetails = [<Label.Detail key="name">{issueStatus.name || "?"}</Label.Detail>]
        if (issueStatus.name && issueTracker?.parameters?.show_issue_creation_date) {
            labelDetails.push(<Label.Detail key="created">Created <TimeAgo date={issueStatus.created}/></Label.Detail>)
        }
        if (issueStatus.name && issueTracker?.parameters?.show_issue_update_date) {
            labelDetails.push(<Label.Detail key="updated">Updated <TimeAgo date={issueStatus.updated}/></Label.Detail>)
        }
        let label = <Label basic={basic} color={color}>{issueStatus.issue_id}{labelDetails}</Label>
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
            label = <Popup content={popupContent} flowing hoverable trigger={label} />
        }
        return <div key={issueStatus.issue_id}>{label}</div>
    });
    return <>{statuses}</>
}
