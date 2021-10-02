import React from 'react';
import { render, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueStatus } from './IssueStatus';

function renderIssueStatus({ showIssueCreationDate = false, updated = false, connectionError = false, parseError = false } = {}) {
    let creationDate = new Date();
    creationDate.setDate(creationDate.getDate() - 4);
    const metric = {
        issue_status: [
            {
                issue_id: "123",
                name: "in progress",
                landing_url: "https://test",
                created: creationDate.toISOString(),
            }
        ]
    }
    if (connectionError) {
        metric.issue_status[0].connection_error = "error";
    }
    if (parseError) {
        metric.issue_status[0].parse_error = "error";
    }
    if (updated) {
        let updateDate = new Date();
        updateDate.setDate(updateDate.getDate() - 2);
        metric.issue_status[0].updated = updateDate.toISOString();
    }
    const issueTracker = { parameters: { show_issue_creation_date: showIssueCreationDate } }
    return render(<IssueStatus metric={metric} issueTracker={issueTracker} />)
}

it("displays a link with correct content", async () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/123/)).not.toBe(null)
    expect(queryByText(/123/).closest("a").href).toBe("https://test/")
});

it("displays the creation date in the label if configured", async () => {
    const { queryByText } = renderIssueStatus({ showIssueCreationDate: true })
    expect(queryByText(/4 days ago/)).not.toBe(null)
});

it("does not display the creation date in the label if not configured", async () => {
    const { queryByText } = renderIssueStatus({ showIssueCreationDate: false })
    expect(queryByText(/4 days ago/)).toBe(null)
});

it("displays the creation date in the popup", async () => {
    const { queryByText } = renderIssueStatus({ updated: false })
    userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).not.toBe(null)
        expect(queryByText("2 days ago")).toBe(null);
    })
});

it("displays the update date in the popup", async () => {
    const { queryByText } = renderIssueStatus({ updated: true })
    userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).not.toBe(null);
        expect(queryByText("2 days ago")).not.toBe(null);
    })
});

it("displays a connection error in the popup", async () => {
    const { queryByText } = renderIssueStatus({ connectionError: true })
    userEvent.hover(queryByText(/123/))
    await waitFor(() => { expect(queryByText("Connection error")).not.toBe(null) })
});

it("displays a parse error in the popup", async () => {
    const { queryByText } = renderIssueStatus({ parseError: true })
    userEvent.hover(queryByText(/123/))
    await waitFor(() => { expect(queryByText("Parse error")).not.toBe(null) })
});

it("displays nothing if the metric has no issue status", async () => {
    const metric = {}
    const { queryByText } = render(<IssueStatus metric={metric} />)
    expect(queryByText(/123/)).toBe(null)
});
