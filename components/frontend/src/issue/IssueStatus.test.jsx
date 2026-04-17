import { render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { useSettings } from "../app_ui_settings"
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

function IssueStatusWrapper({ issueTrackerMissing, metric }) {
    const settings = useSettings()
    return <IssueStatus metric={metric} issueTrackerMissing={issueTrackerMissing} settings={settings} />
}

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
    return render(<IssueStatusWrapper metric={metric} issueTrackerMissing={issueTrackerMissing} />)
}

beforeEach(() => {
    history.push("")
})

it("has no accessibility violations", async () => {
    const { container } = renderIssueStatus()
    await expectNoAccessibilityViolations(container)
})

it("displays the issue id", async () => {
    renderIssueStatus()
    expectText(/123/)
})

it("opens the issue landing url", async () => {
    globalThis.open = vi.fn()
    renderIssueStatus()
    clickText(/123/)
    expect(globalThis.open).toHaveBeenCalledWith("https://issue")
})

it("does not open an url if the issue has no landing url", async () => {
    globalThis.open = vi.fn()
    renderIssueStatus({ landingUrl: "" })
    clickText(/123/)
    expect(globalThis.open).not.toHaveBeenCalled()
})

it("displays a question mark as status if the issue has no status", async () => {
    renderIssueStatus({ status: null })
    expectText(/\?/)
})

it("displays the issue summary in the label if configured", async () => {
    history.push("?show_issue_summary=true")
    renderIssueStatus()
    expectText(/summary/)
})

it("displays the creation date in the label if configured", async () => {
    history.push("?show_issue_creation_date=true")
    renderIssueStatus()
    expectText(/4 days ago/)
})

it("does not display the creation date in the label if not configured", async () => {
    renderIssueStatus()
    expectNoText(/4 days ago/)
})

it("displays the issue summary in the popup", async () => {
    renderIssueStatus()
    await hoverText(/123/)
    await expectTextAfterWait("Issue summary")
})

it("displays the creation date in the popup", async () => {
    renderIssueStatus({ updated: false })
    await hoverText(/123/)
    await expectTextAfterWait(/4 days ago/)
    expectNoText(/2 days ago/)
})

it("displays the update date in the label if configured", async () => {
    history.push("?show_issue_update_date=true")
    renderIssueStatus({ updated: true })
    expectText(/2 days ago/)
})

it("does not display the update date in the label if not configured", async () => {
    renderIssueStatus({ updated: true })
    expectNoText(/2 days ago/)
})

it("displays the update date in the popup", async () => {
    renderIssueStatus({ updated: true })
    await hoverText(/123/)
    await expectTextAfterWait(/4 days ago/)
})

it("displays the due date in the label if configured", async () => {
    history.push("?show_issue_due_date=true")
    renderIssueStatus({ due: true })
    expectText(/in 2 days/)
})

it("does not display the due date in the label if not configured", async () => {
    renderIssueStatus({ due: true })
    expectNoText(/2 days from now/)
})

it("displays the due date in the popup", async () => {
    renderIssueStatus({ due: true })
    await hoverText(/123/)
    await expectTextAfterWait(/in 2 days/)
})

it("displays the planned release in the label if configured", async () => {
    history.push("?show_issue_release=true")
    renderIssueStatus({ release: true })
    expectText(/1.0/)
    expectText(/planned/)
    expectText(/in \d+ years/)
})

it("displays the released release in the label if configured", async () => {
    history.push("?show_issue_release=true")
    renderIssueStatus({ release: true, releaseReleased: true })
    expectText(/1.0/)
    expectText(/released/)
    expectText(/in \d+ years/)
})

it("displays the release in the label if configured, but without release date", async () => {
    history.push("?show_issue_release=true")
    renderIssueStatus({ release: true, releaseDate: null })
    expectText(/1.0/)
    expectText(/planned/)
    expectNoText(/from now/)
})

it("displays the release without doubling release in the label", async () => {
    history.push("?show_issue_release=true")
    renderIssueStatus({ release: true, releaseName: "Release 1.0" })
    expectText(/Release 1.0/)
    expectNoText(/Release Release 1.0/)
})

it("does not display the release in the label if not configured", async () => {
    renderIssueStatus({ release: true })
    expectNoText(/1.0/)
    expectNoText(/planned/)
    expectNoText(/from now/)
})

it("displays the release in the popup", async () => {
    renderIssueStatus({ release: true })
    await hoverText(/123/)
    await expectTextAfterWait(/1.0/)
    expectText(/planned/)
    expectText(/in \d+ years/)
})

it("displays the release in the popup without release date", async () => {
    renderIssueStatus({ release: true, releaseDate: null })
    await hoverText(/123/)
    await expectTextAfterWait(/1.0/)
    expectNoText(/planned/)
    expectNoText(/from now/)
})

it("displays the sprint in the label if configured", async () => {
    history.push("?show_issue_sprint=true")
    renderIssueStatus({ sprint: true })
    expectText(/Sprint 42/)
    expectText(/active/)
    expectText(/in \d+ years/)
})

it("displays the sprint in the label if configured, but without sprint end date", async () => {
    history.push("?show_issue_sprint=true")
    renderIssueStatus({ sprint: true, sprintEndDate: null })
    expectText(/Sprint 42/)
    expectText(/active/)
    expectNoText(/from now/)
})

it("does not display the sprint in the label if not configured", async () => {
    renderIssueStatus({ sprint: true })
    expectNoText(/Sprint 42/)
    expectNoText(/active/)
    expectNoText(/from now/)
})

it("displays the sprint in the popup", async () => {
    renderIssueStatus({ sprint: true })
    await hoverText(/123/)
    await expectTextAfterWait(/Sprint 42/)
    expectText(/active/)
    expectText(/in \d+ years/)
})

it("displays the sprint in the popup without sprint end date", async () => {
    renderIssueStatus({ sprint: true, sprintEndDate: null })
    await hoverText(/123/)
    await expectTextAfterWait(/Sprint 42/)
    expectText(/active/)
    expectNoText(/from now/)
})

it("displays no popup if the issue has no creation date and there is no error", async () => {
    renderIssueStatus({ created: false })
    await hoverText(/123/)
    await expectNoTextAfterWait("4 days ago")
    expectNoText("2 days ago")
    expectNoText("2 days from now")
})

it("displays a connection error in the popup", async () => {
    renderIssueStatus({ connectionError: true })
    await hoverText(/123/)
    await expectTextAfterWait("Connection error")
})

it("displays a parse error in the popup", async () => {
    renderIssueStatus({ parseError: true })
    await hoverText(/123/)
    await expectTextAfterWait("Parse error")
})

it("displays nothing if the metric has no issue status", async () => {
    render(<IssueStatus metric={{}} />)
    expectNoText(/123/)
})

it("displays an error message if the metric has issue ids but the report has no issue tracker", async () => {
    renderIssueStatus({ issueTrackerMissing: true })
    await hoverText(/123/)
    await expectTextAfterWait(/No issue tracker configured/)
})
