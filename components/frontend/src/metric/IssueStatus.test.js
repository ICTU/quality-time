import React from 'react';
import { render } from '@testing-library/react';
import { IssueStatus } from './IssueStatus';

it("displays a link with correct content and popup", async () => {
    const metric = {
        issue_status: [{ issue_id: "123", name: "in progress", description: "doing", landing_url: "https://test" }]
    }
    const statusText = metric.issue_status[0].issue_id + ": " + metric.issue_status[0].name
    const { queryByText } = render(<IssueStatus metric={metric} />)
    expect(queryByText(statusText)).not.toBe(null)
    expect(queryByText(statusText).closest("a").href).toBe("https://test/")
});

it("displays a connection error", async () => {
    const metric = { issue_status: [{ issue_id: "123", connection_error: "error" }] }
    const { queryByTestId } = render(<IssueStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).not.toBe(null)
});

it("displays a parse error", async () => {
    const metric = { issue_status: [{ issue_id: "123", parse_error: "error" }] }
    const { queryByTestId } = render(<IssueStatus metric={metric} />)
    expect(queryByTestId("errorlabel")).not.toBe(null)
});

it("displays nothing if the metric has no issue status", async () => {
    const metric = { }
    const { queryByText } = render(<IssueStatus metric={metric} />)
    expect(queryByText(/123/)).toBe(null)
});
