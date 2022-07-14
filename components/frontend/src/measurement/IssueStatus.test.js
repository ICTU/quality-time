import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueStatus } from './IssueStatus';

function renderIssueStatus(
    {
        connectionError = false,
        created = true,
        due = false,
        issueTrackerMissing = false,
        landingUrl = "https://issue",
        parseError = false,
        status = "in progress",
        statusCategory = "",
        showIssueCreationDate = false,
        showIssueSummary = false,
        showIssueUpdateDate = false,
        showIssueDueDate = false,
        updated = false,
    } = {}
) {
    let creationDate = new Date();
    creationDate.setDate(creationDate.getDate() - 4);
    let updateDate = new Date();
    updateDate.setDate(updateDate.getDate() - 2);
    let dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 2);
    const issueStatus = {
        issue_id: "123",
        name: status,
        summary: "Issue summary",
        created: created ? creationDate.toISOString() : null,
        updated: updated ? updateDate.toISOString() : null,
        duedate: due ? dueDate.toISOString() : null,
        landing_url: landingUrl,
        connection_error: connectionError ? "error" : null,
        parse_error: parseError ? "error" : null,
    }
    if (statusCategory) {
        issueStatus["status_category"] = statusCategory
    }
    const metric = {
        issue_ids: ["123"],
        issue_status: [issueStatus]
    }
    return render(
        <IssueStatus
            metric={metric}
            issueTrackerMissing={issueTrackerMissing}
            showIssueCreationDate={showIssueCreationDate}
            showIssueSummary={showIssueSummary}
            showIssueUpdateDate={showIssueUpdateDate}
            showIssueDueDate={showIssueDueDate}
        />
    )
}

it("displays the issue id", () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/123/)).not.toBe(null)
});

it("displays the status", () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/in progress/)).not.toBe(null)
});

it("displays the status category doing", () => {
    renderIssueStatus({ statusCategory: "doing" });
    expect(screen.getByText(/123/).className).toContain("blue")
});

it("displays the status category todo", () => {
    renderIssueStatus({ statusCategory: "todo" });
    expect(screen.getByText(/123/).className).toContain("grey")
});

it("displays the status category done", () => {
    renderIssueStatus({ statusCategory: "done" });
    expect(screen.getByText(/123/).className).toContain("green")
});

it("displays a missing status category as todo", () => {
    renderIssueStatus();
    expect(screen.getByText(/123/).className).toContain("grey")
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

it("displays the issue summary in the label if configured", async () => {
    const { queryByText } = renderIssueStatus({ showIssueSummary: true })
    expect(queryByText(/summary/)).not.toBe(null)
});

it("displays the creation date in the label if configured", async () => {
    const { queryByText } = renderIssueStatus({ showIssueCreationDate: true })
    expect(queryByText(/4 days ago/)).not.toBe(null)
});

it("does not display the creation date in the label if not configured", async () => {
    const { queryByText } = renderIssueStatus()
    expect(queryByText(/4 days ago/)).toBe(null)
});

it("displays the issue summary in the popup", async () => {
    const { queryByText } = renderIssueStatus()
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("Issue summary")).not.toBe(null)
    })
});

it("displays the creation date in the popup", async () => {
    const { queryByText } = renderIssueStatus({ updated: false })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).not.toBe(null)
        expect(queryByText("2 days ago")).toBe(null);
    })
});

it("displays the update date in the label if configured", async () => {
    const { queryByText } = renderIssueStatus({ updated: true, showIssueUpdateDate: true })
    expect(queryByText(/2 days ago/)).not.toBe(null)
});

it("does not display the update date in the label if not configured", async () => {
    const { queryByText } = renderIssueStatus({ updated: true })
    expect(queryByText(/2 days ago/)).toBe(null)
});

it("displays the update date in the popup", async () => {
    const { queryByText } = renderIssueStatus({ updated: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).not.toBe(null);
        expect(queryByText("2 days ago")).not.toBe(null);
    })
});

it("displays the due date in the label if configured", async () => {
    const { queryByText } = renderIssueStatus({ due: true, showIssueDueDate: true })
    expect(queryByText(/2 days from now/)).not.toBe(null)
});

it("does not display the due date in the label if not configured", async () => {
    const { queryByText } = renderIssueStatus({ due: true })
    expect(queryByText(/2 days from now/)).toBe(null)
});

it("displays the due date in the popup", async () => {
    const { queryByText } = renderIssueStatus({ due: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("2 days from now")).not.toBe(null);
    })
});

it("displays no popup if the issue has no creation date and there is no error", async () => {
    const { queryByText } = renderIssueStatus({ created: false })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => {
        expect(queryByText("4 days ago")).toBe(null);
        expect(queryByText("2 days ago")).toBe(null);
        expect(queryByText("2 days from now")).toBe(null);
    })
})

it("displays a connection error in the popup", async () => {
    const { queryByText } = renderIssueStatus({ connectionError: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => { expect(queryByText("Connection error")).not.toBe(null) })
});

it("displays a parse error in the popup", async () => {
    const { queryByText } = renderIssueStatus({ parseError: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => { expect(queryByText("Parse error")).not.toBe(null) })
});

it("displays nothing if the metric has no issue status", async () => {
    const { queryByText } = render(<IssueStatus metric={{}} />)
    expect(queryByText(/123/)).toBe(null)
});

it("displays an error message if the metric has issue ids but the report has no issue tracker", async () => {
    const { queryByText } = renderIssueStatus({ issueTrackerMissing: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(() => { expect(queryByText(/No issue tracker configured/)).not.toBe(null) })
})
