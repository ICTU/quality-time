import React from 'react';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueTrackerStatus({ metric }) {
    if (!metric.issue_id || !metric.issue_status) { return null }
    let issue_statuses = [metric.issue_status]
    return issue_statuses.map((issue_status) => {
        const label_text = metric.issue_id + ": " + (issue_status.name || "?");
        const label = issue_status.landing_url ? <HyperLink url={issue_status.landing_url}>{label_text}</HyperLink> : label_text;
        const error = issue_status.connection_error ? "Connection error" : "Parse error";
        return (
            <Popup
                flowing hoverable
                trigger={issue_status.connection_error || issue_status.parse_error ? <Label data-testid="errorlabel" color='red'>{label}</Label> : <div>{label}</div>}>
                {issue_status.description || error}
            </Popup>
        )
    })
}
