import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { asyncClickText, clickText, expectNoAccessibilityViolations, expectSearch } from "../testUtils"
import { SettingsPanel } from "./SettingsPanel"

beforeEach(() => {
    history.push("")
})

function renderSettingsPanel({
    atReportsOverview = true,
    handleDateChange = vi.fn(),
    handleSort = vi.fn(),
    reportDate = null,
    tags = [],
} = {}) {
    const settings = createTestableSettings()
    return render(
        <SettingsPanel
            atReportsOverview={atReportsOverview}
            handleDateChange={handleDateChange}
            handleSort={handleSort}
            settings={{
                hiddenCards: settings.hiddenCards,
                hiddenColumns: settings.hiddenColumns,
                hiddenTags: settings.hiddenTags,
                hideEmptyColumns: settings.hideEmptyColumns,
                metricsToHide: settings.metricsToHide,
                nrDates: settings.nrDates,
                showIssueCreationDate: settings.showIssueCreationDate,
                showIssueSummary: settings.showIssueSummary,
                showIssueUpdateDate: settings.showIssueUpdateDate,
                showIssueDueDate: settings.showIssueDueDate,
                showIssueRelease: settings.showIssueRelease,
                showIssueSprint: settings.showIssueSprint,
                sortColumn: settings.sortColumn,
                sortDirection: settings.sortDirection,
                expandedItems: settings.expandedItems,
            }}
            reportDate={reportDate}
            tags={tags}
        />,
    )
}

it("hides the metrics not requiring action", async () => {
    const { container } = renderSettingsPanel()
    clickText(/Metrics requiring action/)
    expectSearch("?metrics_to_hide=no_action_required")
    await expectNoAccessibilityViolations(container)
})

it("shows all metrics", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderSettingsPanel()
    clickText(/All metrics/)
    expectSearch("")
})

it("shows all metrics by keypress", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderSettingsPanel()
    await userEvent.type(screen.getByText(/All metrics/), " ")
    expectSearch("")
})

it("hides a tag", async () => {
    renderSettingsPanel({ tags: ["security"] })
    clickText(/security/)
    expectSearch("?hidden_tags=security")
})

it("hides a tag by keypress", async () => {
    renderSettingsPanel({ tags: ["security"] })
    await userEvent.type(screen.getAllByText(/security/)[0], " ")
    expectSearch("?hidden_tags=security")
})

it("shows a tag", async () => {
    history.push("?hidden_tags=security")
    renderSettingsPanel({ tags: ["security"] })
    clickText(/security/, 0)
    expectSearch("")
})

it("hides a column", async () => {
    renderSettingsPanel()
    clickText(/Trend/)
    expectSearch("?hidden_columns=trend")
})

it("hides a column by keypress", async () => {
    renderSettingsPanel()
    await userEvent.type(screen.getAllByText(/Comment/)[0], " ")
    expectSearch("?hidden_columns=comment")
})

it("shows a column", async () => {
    history.push("?hidden_columns=status")
    renderSettingsPanel()
    clickText(/Status/, 0)
    expectSearch("")
})

it("hides empty columns", async () => {
    renderSettingsPanel()
    clickText(/Empty columns/)
    expectSearch("?hide_empty_columns=true")
})

it("show empty columns", async () => {
    history.push("?hide_empty_columns=true")
    renderSettingsPanel()
    clickText(/Empty columns/)
    expectSearch("")
})

it("changes the sorting of an unsorted column", async () => {
    const handleSort = vi.fn()
    renderSettingsPanel({ handleSort: handleSort })
    clickText(/Comment/, 1)
    expect(handleSort).toHaveBeenCalledWith("comment")
})

Array("ascending", "descending").forEach((sortOrder) => {
    it("changes the sorting of a column", async () => {
        history.push(`?sort_column=comment&sort_direction=${sortOrder}`)
        const handleSort = vi.fn()
        renderSettingsPanel({ handleSort: handleSort })
        clickText(/Comment/, 1)
        expect(handleSort).toHaveBeenCalledWith("comment")
    })
})

it("sorts a column by keypress", async () => {
    const handleSort = vi.fn()
    renderSettingsPanel({ handleSort: handleSort })
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("shows issue summaries", async () => {
    renderSettingsPanel()
    await asyncClickText(/Summary/, 0)
    expectSearch("?show_issue_summary=true")
})

it("shows issue summaries by keypress", async () => {
    renderSettingsPanel()
    await userEvent.type(screen.getAllByText(/Summary/)[0], " ")
    expectSearch("?show_issue_summary=true")
})

it("hides the reports cards", async () => {
    renderSettingsPanel()
    await asyncClickText(/Reports/)
    expectSearch("?hidden_cards=reports")
})

it("hides the subject cards", async () => {
    renderSettingsPanel({ atReportsOverview: false })
    await asyncClickText(/Subjects/)
    expectSearch("?hidden_cards=subjects")
})

it("hides the tag cards", async () => {
    renderSettingsPanel()
    await asyncClickText(/Tag/, 0)
    expectSearch("?hidden_cards=tags")
})
