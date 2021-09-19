import React from 'react';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueStatus({ metric }) {
    const issue_statuses = metric.issue_status || [];
    const statuses = issue_statuses.map((issue_status) => {
        let label_text = issue_status.issue_id + ": " + (issue_status.name || "?");
        let label = issue_status.landing_url ? <HyperLink url={issue_status.landing_url}>{label_text}</HyperLink> : label_text;
        let error = issue_status.connection_error ? "Connection error" : "Parse error";
        return (
            <div key={issue_status.issue_id}>
                <Popup
                    flowing hoverable
                    trigger={issue_status.connection_error || issue_status.parse_error ? <Label data-testid="errorlabel" color='red'>{label}</Label> : <div>{label}</div>}>
                    {issue_status.description || error}
                </Popup>
            </div>
        )
    });
    return (
        <>{statuses}</>
    )
}
