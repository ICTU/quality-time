import React from 'react';
import { render } from '@testing-library/react';
import { IssueTrackerStatus } from './IssueTrackerStatus';

it("Displays a loader", () => {
    const { queryByTestId } = render(<IssueTrackerStatus issueStatus={{loading: true}}/>)
    expect(queryByTestId("issue-tracker-loader")).not.toBe(null)
})

it("Displays a link with correct content and popup.", async () => {
    const metric = {tracker_issue: "123",}
    const issueStatus = {
        name: "in progress",
        description: "all is well",
        landing_url: "https://test-url/"
    }
    const statusText = metric.tracker_issue + ": " + issueStatus.name
    const { queryByText } = render(<IssueTrackerStatus metric={metric} issueStatus={issueStatus}/>)
    expect(queryByText(statusText)).not.toBe(null)
    expect(queryByText(statusText).closest("a").href).toBe("https://test-url/")
})

it("Displays an error in red.", async () => {
    const metric = {tracker_issue: "123",}
    const issueStatus = {
        name: "error",
        description: "something went wrong",
    }
    const { queryByTestId } = render(<IssueTrackerStatus metric={metric} issueStatus={issueStatus}/>)
    expect(queryByTestId("errorlabel")).not.toBe(null)
})