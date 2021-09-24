import React from 'react';
import TimeAgo from 'react-timeago';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueStatus({ metric }) {
    const issueStatuses = metric.issue_status || [];
    const statuses = issueStatuses.map((issueStatus) => {
        let label = issueStatus.issue_id + ": " + (issueStatus.name || "?"); 
        if (issueStatus.landing_url) { label = <HyperLink url={issueStatus.landing_url}>{label}</HyperLink> }
        if (issueStatus.created) { label = <>{label} (created <TimeAgo date={issueStatus.created}/>)</>}
        let error = "";
        if (issueStatus.connection_error) { error = "Connection error" }
        if (issueStatus.parse_error) { error = "Parse error" }
        if (error) { label = <Popup content={error} flowing hoverable trigger={<Label color="red">{label}</Label>} /> }
        return <div key={issueStatus.issue_id}>{label}</div>
    });
    return <>{statuses}</>
}
