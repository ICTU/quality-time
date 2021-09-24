import React from 'react';
import TimeAgo from 'react-timeago';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueStatus({ metric }) {
    const issueStatuses = metric.issue_status || [];
    const statuses = issueStatuses.map((issueStatus) => {
        let popupContent = "";
        if (issueStatus.connection_error) { popupContent = "Connection error" }
        if (issueStatus.parse_error) { popupContent = "Parse error" }
        const color = popupContent ? "red" : "grey";
        const basic = popupContent ? false : true;
        let label = <Label basic={basic} color={color}>{issueStatus.issue_id}<Label.Detail>{issueStatus.name || "?"}</Label.Detail></Label>
        if (issueStatus.landing_url) {
            // Without the span, the popup doesn't work
            label = <span><HyperLink url={issueStatus.landing_url}>{label}</HyperLink></span>
        }
        if (!popupContent && issueStatus.created) {
            const creationDate = new Date(issueStatus.created);
            popupContent = <>Created <TimeAgo date={issueStatus.created}/> ({creationDate.toLocaleString()})</>
        }
        if (popupContent){
            label = <Popup content={popupContent} flowing hoverable trigger={label} />
        }
        return <div key={issueStatus.issue_id}>{label}</div>
    });
    return <>{statuses}</>
}
