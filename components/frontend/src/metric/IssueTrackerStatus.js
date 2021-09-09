import React from 'react';
import { Label, Loader, Popup } from 'semantic-ui-react';
import { HyperLink } from '../widgets/HyperLink';

export function IssueTrackerStatus({metric, issueStatus}) {
    if (issueStatus.loading){
        return <Loader data-testid="issue-tracker-loader" active inline />
    }
    const trackerIssueText = metric.tracker_issue + ": " + issueStatus.name;
    function source_label() {
        return (issueStatus.landing_url ? <HyperLink url={issueStatus.landing_url}>{trackerIssueText}</HyperLink> : trackerIssueText)
    }
    return (
        <Popup
            flowing hoverable
            trigger={issueStatus.name.toLowerCase().includes("error") ? <Label data-testid="errorlabel" color='red'>{source_label()}</Label> : <div>{source_label()}</div>}>
            {issueStatus.description}
        </Popup>
    )
}
