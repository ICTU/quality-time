import React from 'react';
import { render, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueStatus } from './IssueStatus';

it("displays a link with correct content", async () => {
    const metric = { issue_status: [{ issue_id: "123", name: "in progress", landing_url: "https://test" }] }
    const label = metric.issue_status[0].issue_id + ": " + metric.issue_status[0].name
    const { queryByText } = render(<IssueStatus metric={metric} />)
    expect(queryByText(label)).not.toBe(null)
    expect(queryByText(label).closest("a").href).toBe("https://test/")
});

it("displays a connection error", async () => {
    const metric = { issue_status: [{ issue_id: "123", connection_error: "error" }] }
    const { queryByText } = render(<IssueStatus metric={metric} />)
    userEvent.hover(queryByText(/123: ?/))
    await waitFor(() => { expect(queryByText("Connection error")).not.toBe(null) })
});

it("displays a parse error", async () => {
    const metric = { issue_status: [{ issue_id: "123", parse_error: "error" }] }
    const { queryByText } = render(<IssueStatus metric={metric} />)
    userEvent.hover(queryByText(/123: ?/))
    await waitFor(() => { expect(queryByText("Parse error")).not.toBe(null) })
});

it("displays nothing if the metric has no issue status", async () => {
    const metric = {}
    const { queryByText } = render(<IssueStatus metric={metric} />)
    expect(queryByText(/123/)).toBe(null)
});
