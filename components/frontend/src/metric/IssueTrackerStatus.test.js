import React from 'react';
import { render } from '@testing-library/react';
import { IssueTrackerStatus } from './IssueTrackerStatus';

it("displays a link with correct content and popup", async () => {
    const metric = {
        issue_id: "123",
        issue_status: {issue: "123", name: "in progress", description: "doing", landing_url: "https://test"}
    }
    const statusText = metric.issue_id + ": " + metric.issue_status.name
    const { queryByText } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByText(statusText)).not.toBe(null)
    expect(queryByText(statusText).closest("a").href).toBe("https://test/")
});

it("displays a connection error", async () => {
    const metric = {issue_id: "123", issue_status: {issue: "123", connection_error: "error"}}
    const { queryByTestId } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).not.toBe(null)
});

it("displays a parse error", async () => {
    const metric = {issue_id: "123", issue_status: {issue: "123", parse_error: "error"}}
    const { queryByTestId } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).not.toBe(null)
});

it("displays nothing if the metric has no metric id", async () => {
    const metric = {
        issue_status: {issue: "123", name: "in progress", description: "doing", landing_url: "https://test"}
    }
    const { queryByTestId } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).toBe(null)
});

it("displays nothing if the metric has no issue startus", async () => {
    const metric = { issue_id: "123" }
    const { queryByTestId } = render(<IssueTrackerStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).toBe(null)
});
