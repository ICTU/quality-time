import React from 'react';
import { render, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueStatus } from './IssueStatus';

function renderIssueStatus(
    {
        status = "in progress",
        landingUrl = "https://issue",
        showIssueCreationDate = false,
        showIssueUpdateDate = false,
        created = true,
        updated = false,
        connectionError = false,
        parseError = false
    } = {}
) {
    let creationDate = new Date();
    creationDate.setDate(creationDate.getDate() - 4);
    let updateDate = new Date();
    updateDate.setDate(updateDate.getDate() - 2);
    const metric = {
        issue_status: [
            {
                issue_id: "123",
                name: status,
                created: created ? creationDate.toISOString() : null,
                updated: updated ? updateDate.toISOString() : null,
                landing_url: landingUrl,
                connection_error: connectionError ? "error" : null,
                parse_error: parseError ? "error" : null,
            }
        ]
    }
    const issueTracker = {
        parameters: {
            show_issue_creation_date: showIssueCreationDate,
            show_issue_update_date: showIssueUpdateDate
        }
    }
    return render(<IssueStatus metric={metric} issueTracker={issueTracker} />)
}

it("displays the issue id", () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/123/)).not.toBe(null)
});

it("displays the status", () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/in progress/)).not.toBe(null)
});

it("displays the issue landing url", async () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/123/).closest("a").href).toBe("https://issue/")
});

it("does not display an url if the issue has no landing url", async () => {
    const { queryByText } = renderIssueStatus({ landingUrl: null })
    expect(queryByText(/123/).closest("a")).toBe(null)
});

it("displays a question mark as status if the issue has no status", () => {
    const { queryByText } = renderIssueStatus({ status: null })
    expect(queryByText(/\?/)).not.toBe(null)
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

it("displays the update date in the label if configured", async () => {
    const { queryByText } = renderIssueStatus({ showIssueUpdateDate: true, updated: true })
    expect(queryByText(/2 days ago/)).not.toBe(null)
});

it("does not display the update date in the label if not configured", async () => {
    const { queryByText } = renderIssueStatus({ showIssueUpdateDate: false, updated: true })
    expect(queryByText(/2 days ago/)).toBe(null)
});

it("displays the update date in the popup", async () => {
    const { queryByText } = renderIssueStatus({ updated: true })
    userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).not.toBe(null);
        expect(queryByText("2 days ago")).not.toBe(null);
    })
});

it("displays no popup if the issue has no creation date and there is no error", async () => {
    const { queryByText } = renderIssueStatus({ created: false })
    userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).toBe(null);
        expect(queryByText("2 days ago")).toBe(null);
    })
})

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
    const { queryByText } = render(<IssueStatus metric={{}} />)
    expect(queryByText(/123/)).toBe(null)
});
