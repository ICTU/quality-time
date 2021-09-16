import React from 'react';
import { render } from '@testing-library/react';
import { IssueTrackerStatus } from './IssueTrackerStatus';

it("displays a link with correct content and popup.", async () => {
    const metric = {
        tracker_issue: "123", 
        issue_status: {issue: "123", name: "in progress", description: "doing", landing_url: "https://test"}
    }
    const statusText = metric.tracker_issue + ": " + metric.issue_status.name
    const { queryByText } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByText(statusText)).not.toBe(null)
    expect(queryByText(statusText).closest("a").href).toBe("https://test/")
});

it("displays an error in red.", async () => {
    const metric = {tracker_issue: "123", issue_status: {issue: "123", parse_error: "error"}}
    const { queryByTestId } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).not.toBe(null)
});
