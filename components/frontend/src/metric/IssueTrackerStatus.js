import React from 'react';
import { Label, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueTrackerStatus({ metric }) {
    const label_text = metric.issue_id + ": " + (metric.issue_status.name || "?");
    const label = metric.issue_status.landing_url ? <HyperLink url={metric.issue_status.landing_url}>{label_text}</HyperLink> : label_text;
    const error = metric.issue_status?.connection_error ? "Connection error" : "Parse error";
    return (
        <Popup
            flowing hoverable
            trigger={metric.issue_status?.connection_error || metric.issue_status?.parse_error ? <Label data-testid="errorlabel" color='red'>{label}</Label> : <div>{label}</div>}>
            {metric.issue_status.description || error}
        </Popup>
    )
}
