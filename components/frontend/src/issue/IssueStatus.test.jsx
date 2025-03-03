import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { expectNoAccessibilityViolations } from "../testUtils"
import { IssueStatus } from "./IssueStatus"

function renderIssueStatus({
    connectionError = false,
    created = true,
    due = false,
    issueTrackerMissing = false,
    landingUrl = "https://issue",
    parseError = false,
    status = "in progress",
    statusCategory = "",
    release = false,
    releaseName = "1.0",
    releaseReleased = false,
    releaseDate = "3000-01-02",
    sprint = false,
    sprintEndDate = "3000-01-01",
    updated = false,
} = {}) {
    const settings = createTestableSettings()
    let creationDate = new Date()
    creationDate.setDate(creationDate.getDate() - 4)
    let updateDate = new Date()
    updateDate.setDate(updateDate.getDate() - 2)
    let dueDate = new Date()
    dueDate.setDate(dueDate.getDate() + 2)
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
        release_name: release ? releaseName : null,
        release_released: release ? releaseReleased : null,
        release_date: release ? releaseDate : null,
        sprint_name: sprint ? "Sprint 42" : null,
        sprint_state: sprint ? "active" : null,
        sprint_enddate: sprint ? sprintEndDate : null,
    }
    if (statusCategory) {
        issueStatus["status_category"] = statusCategory
    }
    const metric = {
        issue_ids: ["123"],
        issue_status: [issueStatus],
    }
    return render(<IssueStatus metric={metric} issueTrackerMissing={issueTrackerMissing} settings={settings} />)
}

beforeEach(() => {
    history.push("")
})

it("displays the issue id", async () => {
    const { container } = renderIssueStatus()
    expect(screen.queryByText(/123/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("opens the issue landing url", async () => {
    window.open = vi.fn()
    const { container, queryByText } = renderIssueStatus()
    fireEvent.click(queryByText(/123/))
    expect(window.open).toHaveBeenCalledWith("https://issue")
    await expectNoAccessibilityViolations(container)
})

it("does not open an url if the issue has no landing url", async () => {
    window.open = vi.fn()
    const { container, queryByText } = renderIssueStatus({ landingUrl: "" })
    fireEvent.click(queryByText(/123/))
    expect(window.open).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("displays a question mark as status if the issue has no status", async () => {
    const { container, queryByText } = renderIssueStatus({ status: null })
    expect(queryByText(/\?/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the issue summary in the label if configured", async () => {
    history.push("?show_issue_summary=true")
    const { container, queryByText } = renderIssueStatus()
    expect(queryByText(/summary/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the creation date in the label if configured", async () => {
    history.push("?show_issue_creation_date=true")
    const { container, queryByText } = renderIssueStatus()
    expect(queryByText(/4 days ago/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not display the creation date in the label if not configured", async () => {
    const { container, queryByText } = renderIssueStatus()
    expect(queryByText(/4 days ago/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the issue summary in the popup", async () => {
    const { container, queryByText } = renderIssueStatus()
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText("Issue summary")).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the creation date in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ updated: false })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/4 days ago/)).not.toBe(null)
        expect(queryByText(/2 days ago/)).toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the update date in the label if configured", async () => {
    history.push("?show_issue_update_date=true")
    const { container, queryByText } = renderIssueStatus({ updated: true })
    expect(queryByText(/2 days ago/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not display the update date in the label if not configured", async () => {
    const { container, queryByText } = renderIssueStatus({ updated: true })
    expect(queryByText(/2 days ago/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the update date in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ updated: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/4 days ago/)).not.toBe(null)
        expect(queryByText(/2 days ago/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the due date in the label if configured", async () => {
    history.push("?show_issue_due_date=true")
    const { container, queryByText } = renderIssueStatus({ due: true })
    expect(queryByText(/in 2 days/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not display the due date in the label if not configured", async () => {
    const { container, queryByText } = renderIssueStatus({ due: true })
    expect(queryByText(/2 days from now/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the due date in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ due: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/in 2 days/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the planned release in the label if configured", async () => {
    history.push("?show_issue_release=true")
    const { container, queryByText } = renderIssueStatus({ release: true })
    expect(queryByText(/1.0/)).not.toBe(null)
    expect(queryByText(/planned/)).not.toBe(null)
    expect(queryByText(/in \d+ years/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the released release in the label if configured", async () => {
    history.push("?show_issue_release=true")
    const { container, queryByText } = renderIssueStatus({ release: true, releaseReleased: true })
    expect(queryByText(/1.0/)).not.toBe(null)
    expect(queryByText(/released/)).not.toBe(null)
    expect(queryByText(/in \d+ years/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the release in the label if configured, but without release date", async () => {
    history.push("?show_issue_release=true")
    const { container, queryByText } = renderIssueStatus({ release: true, releaseDate: null })
    expect(queryByText(/1.0/)).not.toBe(null)
    expect(queryByText(/planned/)).not.toBe(null)
    expect(queryByText(/from now/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the release without doubling release in the label", async () => {
    history.push("?show_issue_release=true")
    const { container, queryByText } = renderIssueStatus({ release: true, releaseName: "Release 1.0" })
    expect(queryByText(/Release 1.0/)).not.toBe(null)
    expect(queryByText(/Release Release 1.0/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not display the release in the label if not configured", async () => {
    const { container, queryByText } = renderIssueStatus({ release: true })
    expect(queryByText(/1.0/)).toBe(null)
    expect(queryByText(/planned/)).toBe(null)
    expect(queryByText(/from now/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the release in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ release: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/1.0/)).not.toBe(null)
        expect(queryByText(/planned/)).not.toBe(null)
        expect(queryByText(/in \d+ years/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the release in the popup without release date", async () => {
    const { container, queryByText } = renderIssueStatus({ release: true, releaseDate: null })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/1.0/)).not.toBe(null)
        expect(queryByText(/planned/)).toBe(null)
        expect(queryByText(/from now/)).toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the sprint in the label if configured", async () => {
    history.push("?show_issue_sprint=true")
    const { container, queryByText } = renderIssueStatus({ sprint: true })
    expect(queryByText(/Sprint 42/)).not.toBe(null)
    expect(queryByText(/active/)).not.toBe(null)
    expect(queryByText(/in \d+ years/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the sprint in the label if configured, but without sprint end date", async () => {
    history.push("?show_issue_sprint=true")
    const { container, queryByText } = renderIssueStatus({ sprint: true, sprintEndDate: null })
    expect(queryByText(/Sprint 42/)).not.toBe(null)
    expect(queryByText(/active/)).not.toBe(null)
    expect(queryByText(/from now/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not display the sprint in the label if not configured", async () => {
    const { container, queryByText } = renderIssueStatus({ sprint: true })
    expect(queryByText(/Sprint 42/)).toBe(null)
    expect(queryByText(/active/)).toBe(null)
    expect(queryByText(/from now/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays the sprint in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ sprint: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/Sprint 42/)).not.toBe(null)
        expect(queryByText(/active/)).not.toBe(null)
        expect(queryByText(/in \d+ years/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays the sprint in the popup without sprint end date", async () => {
    const { container, queryByText } = renderIssueStatus({ sprint: true, sprintEndDate: null })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/Sprint 42/)).not.toBe(null)
        expect(queryByText(/active/)).not.toBe(null)
        expect(queryByText(/from now/)).toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays no popup if the issue has no creation date and there is no error", async () => {
    const { container, queryByText } = renderIssueStatus({ created: false })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText("4 days ago")).toBe(null)
        expect(queryByText("2 days ago")).toBe(null)
        expect(queryByText("2 days from now")).toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays a connection error in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ connectionError: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText("Connection error")).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays a parse error in the popup", async () => {
    const { container, queryByText } = renderIssueStatus({ parseError: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText("Parse error")).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("displays nothing if the metric has no issue status", async () => {
    const { container, queryByText } = render(<IssueStatus metric={{}} />)
    expect(queryByText(/123/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("displays an error message if the metric has issue ids but the report has no issue tracker", async () => {
    const { container, queryByText } = renderIssueStatus({ issueTrackerMissing: true })
    await userEvent.hover(queryByText(/123/))
    await waitFor(async () => {
        expect(queryByText(/No issue tracker configured/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})
