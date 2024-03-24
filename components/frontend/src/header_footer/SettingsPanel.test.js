import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { SettingsPanel } from "./SettingsPanel"

beforeEach(() => {
    history.push("")
})

function renderSettingsPanel({
    atReportsOverview = true,
    handleDateChange = jest.fn(),
    handleSort = jest.fn(),
    reportDate = null,
    tags = [],
} = {}) {
    const settings = createTestableSettings()
    render(
        <SettingsPanel
            atReportsOverview={atReportsOverview}
            handleDateChange={handleDateChange}
            handleSort={handleSort}
            settings={{
                dateInterval: settings.dateInterval,
                dateOrder: settings.dateOrder,
                hiddenCards: settings.hiddenCards,
                hiddenColumns: settings.hiddenColumns,
                hiddenTags: settings.hiddenTags,
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
    renderSettingsPanel()
    fireEvent.click(screen.getByText(/Metrics requiring action/))
    expect(history.location.search).toBe("?metrics_to_hide=no_action_needed")
})

it("shows all metrics", async () => {
    history.push("?metrics_to_hide=no_action_needed")
    renderSettingsPanel()
    fireEvent.click(screen.getByText(/All metrics/))
    expect(history.location.search).toBe("")
})

it("shows all metrics by keypress", async () => {
    history.push("?metrics_to_hide=no_action_needed")
    renderSettingsPanel()
    await userEvent.type(screen.getByText(/All metrics/), " ")
    expect(history.location.search).toBe("")
})

it("hides a tag", async () => {
    renderSettingsPanel({ tags: ["security"] })
    fireEvent.click(screen.getByText(/security/))
    expect(history.location.search).toBe("?hidden_tags=security")
})

it("hides a tag by keypress", async () => {
    renderSettingsPanel({ tags: ["security"] })
    await userEvent.type(screen.getAllByText(/security/)[0], " ")
    expect(history.location.search).toBe("?hidden_tags=security")
})

it("shows a tag", async () => {
    history.push("?hidden_tags=security")
    renderSettingsPanel({ tags: ["security"] })
    fireEvent.click(screen.getAllByText(/security/)[0])
    expect(history.location.search).toBe("")
})

it("hides a column", async () => {
    renderSettingsPanel()
    fireEvent.click(screen.getByText(/Trend/))
    expect(history.location.search).toBe("?hidden_columns=trend")
})

it("hides a column by keypress", async () => {
    renderSettingsPanel()
    await userEvent.type(screen.getAllByText(/Comment/)[0], " ")
    expect(history.location.search).toBe("?hidden_columns=comment")
})

it("shows a column", async () => {
    history.push("?hidden_columns=status")
    renderSettingsPanel()
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(history.location.search).toBe("")
})

it("changes the sorting of an unsorted column", async () => {
    const handleSort = jest.fn()
    renderSettingsPanel({ handleSort: handleSort })
    fireEvent.click(screen.getAllByText(/Comment/)[1])
    expect(handleSort).toHaveBeenCalledWith("comment")
})
;["ascending", "descending"].forEach((sortOrder) => {
    it("changes the sorting of a column", async () => {
        history.push(`?sort_column=comment&sort_direction=${sortOrder}`)
        const handleSort = jest.fn()
        renderSettingsPanel({ handleSort: handleSort })
        fireEvent.click(screen.getAllByText(/Comment/)[1])
        expect(handleSort).toHaveBeenCalledWith("comment")
    })
})

it("sorts a column by keypress", async () => {
    const handleSort = jest.fn()
    renderSettingsPanel({ handleSort: handleSort })
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("ignores a keypress if the menu item is disabled", async () => {
    history.push("?hidden_columns=comment")
    const handleSort = jest.fn()
    renderSettingsPanel({ handleSort: handleSort })
    await userEvent.type(screen.getAllByText(/Comment/)[1], " ")
    expect(handleSort).not.toHaveBeenCalledWith("comment")
})

it("sets the number of dates", async () => {
    history.push("?nr_dates=2")
    renderSettingsPanel()
    fireEvent.click(screen.getByText(/7 dates/))
    expect(history.location.search).toBe("?nr_dates=7")
})

it("sets the number of dates by keypress", async () => {
    renderSettingsPanel()
    await userEvent.type(screen.getByText(/5 dates/), " ")
    expect(history.location.search).toBe("?nr_dates=5")
})

it("sets the date interval to weeks", async () => {
    history.push("?nr_dates=2")
    renderSettingsPanel()
    await act(async () => fireEvent.click(screen.getByText(/2 weeks/)))
    expect(history.location.search).toBe("?nr_dates=2&date_interval=14")
})

it("sets the date interval to one day", () => {
    history.push("?nr_dates=2")
    renderSettingsPanel()
    fireEvent.click(screen.getByText(/1 day/))
    expect(history.location.search).toBe("?nr_dates=2&date_interval=1")
})

it("sets the date interval by keypress", async () => {
    history.push("?nr_dates=2&date_interval=7")
    renderSettingsPanel()
    await userEvent.type(screen.getByText(/1 day/), " ")
    expect(history.location.search).toBe("?nr_dates=2&date_interval=1")
})

it("sorts the dates descending", () => {
    history.push("?nr_dates=2&date_order=ascending")
    renderSettingsPanel()
    fireEvent.click(screen.getByText(/Descending/))
    expect(history.location.search).toBe("?nr_dates=2")
})

it("sorts the dates ascending by keypress", async () => {
    history.push("?nr_dates=2")
    renderSettingsPanel()
    await userEvent.type(screen.getByText(/Ascending/), " ")
    expect(history.location.search).toBe("?nr_dates=2&date_order=ascending")
})

it("shows issue summaries", async () => {
    renderSettingsPanel()
    await act(async () => {
        fireEvent.click(screen.getAllByText(/Summary/)[0])
    })
    expect(history.location.search).toBe("?show_issue_summary=true")
})

it("shows issue summaries by keypress", async () => {
    renderSettingsPanel()
    await userEvent.type(screen.getAllByText(/Summary/)[0], " ")
    expect(history.location.search).toBe("?show_issue_summary=true")
})

it("hides the reports cards", async () => {
    renderSettingsPanel()
    await act(async () => fireEvent.click(screen.getByText(/Reports/)))
    expect(history.location.search).toBe("?hidden_cards=reports")
})

it("hides the subject cards", async () => {
    renderSettingsPanel({ atReportsOverview: false })
    await act(async () => fireEvent.click(screen.getByText(/Subjects/)))
    expect(history.location.search).toBe("?hidden_cards=subjects")
})

it("hides the tag cards", async () => {
    renderSettingsPanel()
    await act(async () => fireEvent.click(screen.getAllByText(/Tags/)[0]))
    expect(history.location.search).toBe("?hidden_cards=tags")
})
