import React from 'react';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueStatus({ metric }) {
    const issue_statuses = metric.issue_status || [];
    const statuses = issue_statuses.map((issue_status) => {
        const datePrefix = issue_status.created ? issue_status.created + " - " : ""
        let label = datePrefix + issue_status.issue_id + ": " + (issue_status.name || "?");
        if (issue_status.landing_url) { label = <HyperLink url={issue_status.landing_url}>{label}</HyperLink> }
        let error = "";
        if (issue_status.connection_error) { error = "Connection error" }
        if (issue_status.parse_error) { error = "Parse error" }
        if (error) { label = <Popup content={error} flowing hoverable trigger={<Label color="red">{label}</Label>} /> }
        return <div key={issue_status.issue_id}>{label}</div>
    });
    return <>{statuses}</>
}
