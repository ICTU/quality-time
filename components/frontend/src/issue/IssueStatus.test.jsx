import { render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import {
    clickText,
    expectNoAccessibilityViolations,
    expectNoText,
    expectNoTextAfterWait,
    expectText,
    expectTextAfterWait,
    hoverText,
} from "../testUtils"
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
    expectText(/123/)
    await expectNoAccessibilityViolations(container)
})

it("opens the issue landing url", async () => {
    globalThis.open = vi.fn()
    const { container } = renderIssueStatus()
    clickText(/123/)
    expect(globalThis.open).toHaveBeenCalledWith("https://issue")
    await expectNoAccessibilityViolations(container)
})

it("does not open an url if the issue has no landing url", async () => {
    globalThis.open = vi.fn()
    const { container } = renderIssueStatus({ landingUrl: "" })
    clickText(/123/)
    expect(globalThis.open).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("displays a question mark as status if the issue has no status", async () => {
    const { container } = renderIssueStatus({ status: null })
    expectText(/\?/)
    await expectNoAccessibilityViolations(container)
})

it("displays the issue summary in the label if configured", async () => {
    history.push("?show_issue_summary=true")
    const { container } = renderIssueStatus()
    expectText(/summary/)
    await expectNoAccessibilityViolations(container)
})

it("displays the creation date in the label if configured", async () => {
    history.push("?show_issue_creation_date=true")
    const { container } = renderIssueStatus()
    expectText(/4 days ago/)
    await expectNoAccessibilityViolations(container)
})

it("does not display the creation date in the label if not configured", async () => {
    const { container } = renderIssueStatus()
    expectNoText(/4 days ago/)
    await expectNoAccessibilityViolations(container)
})

it("displays the issue summary in the popup", async () => {
    const { container } = renderIssueStatus()
    await hoverText(/123/)
    await expectTextAfterWait("Issue summary")
    await expectNoAccessibilityViolations(container)
})

it("displays the creation date in the popup", async () => {
    const { container } = renderIssueStatus({ updated: false })
    await hoverText(/123/)
    await expectTextAfterWait(/4 days ago/)
    expectNoText(/2 days ago/)
    await expectNoAccessibilityViolations(container)
})

it("displays the update date in the label if configured", async () => {
    history.push("?show_issue_update_date=true")
    const { container } = renderIssueStatus({ updated: true })
    expectText(/2 days ago/)
    await expectNoAccessibilityViolations(container)
})

it("does not display the update date in the label if not configured", async () => {
    const { container } = renderIssueStatus({ updated: true })
    expectNoText(/2 days ago/)
    await expectNoAccessibilityViolations(container)
})

it("displays the update date in the popup", async () => {
    const { container } = renderIssueStatus({ updated: true })
    await hoverText(/123/)
    await expectTextAfterWait(/4 days ago/)
    await expectNoAccessibilityViolations(container)
})

it("displays the due date in the label if configured", async () => {
    history.push("?show_issue_due_date=true")
    const { container } = renderIssueStatus({ due: true })
    expectText(/in 2 days/)
    await expectNoAccessibilityViolations(container)
})

it("does not display the due date in the label if not configured", async () => {
    const { container } = renderIssueStatus({ due: true })
    expectNoText(/2 days from now/)
    await expectNoAccessibilityViolations(container)
})

it("displays the due date in the popup", async () => {
    const { container } = renderIssueStatus({ due: true })
    await hoverText(/123/)
    await expectTextAfterWait(/in 2 days/)
    await expectNoAccessibilityViolations(container)
})

it("displays the planned release in the label if configured", async () => {
    history.push("?show_issue_release=true")
    const { container } = renderIssueStatus({ release: true })
    expectText(/1.0/)
    expectText(/planned/)
    expectText(/in \d+ years/)
    await expectNoAccessibilityViolations(container)
})

it("displays the released release in the label if configured", async () => {
    history.push("?show_issue_release=true")
    const { container } = renderIssueStatus({ release: true, releaseReleased: true })
    expectText(/1.0/)
    expectText(/released/)
    expectText(/in \d+ years/)
    await expectNoAccessibilityViolations(container)
})

it("displays the release in the label if configured, but without release date", async () => {
    history.push("?show_issue_release=true")
    const { container } = renderIssueStatus({ release: true, releaseDate: null })
    expectText(/1.0/)
    expectText(/planned/)
    expectNoText(/from now/)
    await expectNoAccessibilityViolations(container)
})

it("displays the release without doubling release in the label", async () => {
    history.push("?show_issue_release=true")
    const { container } = renderIssueStatus({ release: true, releaseName: "Release 1.0" })
    expectText(/Release 1.0/)
    expectNoText(/Release Release 1.0/)
    await expectNoAccessibilityViolations(container)
})

it("does not display the release in the label if not configured", async () => {
    const { container } = renderIssueStatus({ release: true })
    expectNoText(/1.0/)
    expectNoText(/planned/)
    expectNoText(/from now/)
    await expectNoAccessibilityViolations(container)
})

it("displays the release in the popup", async () => {
    const { container } = renderIssueStatus({ release: true })
    await hoverText(/123/)
    await expectTextAfterWait(/1.0/)
    expectText(/planned/)
    expectText(/in \d+ years/)
    await expectNoAccessibilityViolations(container)
})

it("displays the release in the popup without release date", async () => {
    const { container } = renderIssueStatus({ release: true, releaseDate: null })
    await hoverText(/123/)
    await expectTextAfterWait(/1.0/)
    expectNoText(/planned/)
    expectNoText(/from now/)
    await expectNoAccessibilityViolations(container)
})

it("displays the sprint in the label if configured", async () => {
    history.push("?show_issue_sprint=true")
    const { container } = renderIssueStatus({ sprint: true })
    expectText(/Sprint 42/)
    expectText(/active/)
    expectText(/in \d+ years/)
    await expectNoAccessibilityViolations(container)
})

it("displays the sprint in the label if configured, but without sprint end date", async () => {
    history.push("?show_issue_sprint=true")
    const { container } = renderIssueStatus({ sprint: true, sprintEndDate: null })
    expectText(/Sprint 42/)
    expectText(/active/)
    expectNoText(/from now/)
    await expectNoAccessibilityViolations(container)
})

it("does not display the sprint in the label if not configured", async () => {
    const { container } = renderIssueStatus({ sprint: true })
    expectNoText(/Sprint 42/)
    expectNoText(/active/)
    expectNoText(/from now/)
    await expectNoAccessibilityViolations(container)
})

it("displays the sprint in the popup", async () => {
    const { container } = renderIssueStatus({ sprint: true })
    await hoverText(/123/)
    await expectTextAfterWait(/Sprint 42/)
    expectText(/active/)
    expectText(/in \d+ years/)
    await expectNoAccessibilityViolations(container)
})

it("displays the sprint in the popup without sprint end date", async () => {
    const { container } = renderIssueStatus({ sprint: true, sprintEndDate: null })
    await hoverText(/123/)
    await expectTextAfterWait(/Sprint 42/)
    expectText(/active/)
    expectNoText(/from now/)
    await expectNoAccessibilityViolations(container)
})

it("displays no popup if the issue has no creation date and there is no error", async () => {
    const { container } = renderIssueStatus({ created: false })
    await hoverText(/123/)
    await expectNoTextAfterWait("4 days ago")
    expectNoText("2 days ago")
    expectNoText("2 days from now")
    await expectNoAccessibilityViolations(container)
})

it("displays a connection error in the popup", async () => {
    const { container } = renderIssueStatus({ connectionError: true })
    await hoverText(/123/)
    await expectTextAfterWait("Connection error")
    await expectNoAccessibilityViolations(container)
})

it("displays a parse error in the popup", async () => {
    const { container } = renderIssueStatus({ parseError: true })
    await hoverText(/123/)
    await expectTextAfterWait("Parse error")
    await expectNoAccessibilityViolations(container)
})

it("displays nothing if the metric has no issue status", async () => {
    const { container } = render(<IssueStatus metric={{}} />)
    expectNoText(/123/)
    await expectNoAccessibilityViolations(container)
})

it("displays an error message if the metric has issue ids but the report has no issue tracker", async () => {
    const { container } = renderIssueStatus({ issueTrackerMissing: true })
    await hoverText(/123/)
    await expectTextAfterWait(/No issue tracker configured/)
    await expectNoAccessibilityViolations(container)
})
