import { fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { ResetSettingsButton } from "./ResetSettingsButton"

beforeEach(() => {
    history.push("")
})

function renderResetSettingsButton({
    atReportsOverview = true,
    handleDateChange = jest.fn(),
    reportDate = null,
    settings = null,
} = {}) {
    render(
        <ResetSettingsButton
            atReportsOverview={atReportsOverview}
            handleDateChange={handleDateChange}
            reportDate={reportDate}
            settings={settings}
        />,
    )
}

it("resets the settings", async () => {
    history.push(
        "?date_interval=2&date_order=ascending&hidden_columns=comment&hidden_tags=tag&" +
            "metrics_to_hide=no_action_required&nr_dates=2&show_issue_creation_date=true&show_issue_summary=true&" +
            "show_issue_update_date=true&show_issue_due_date=true&show_issue_release=true&show_issue_sprint=true&" +
            "sort_column=status&sort_direction=descending&expanded=tab:0&hidden_cards=tags",
    )
    const settings = createTestableSettings()
    const handleDateChange = jest.fn()
    renderResetSettingsButton({
        handleDateChange: handleDateChange,
        reportDate: new Date("2023-01-01"),
        settings: settings,
    })
    fireEvent.click(screen.getAllByLabelText(/Reset reports overview settings/)[0])
    expect(history.location.search).toEqual("")
    expect(handleDateChange).toHaveBeenCalledWith(null)
})

it("does not reset the settings when all have the default value", async () => {
    const settings = createTestableSettings()
    const handleDateChange = jest.fn()
    renderResetSettingsButton({
        atReportsOverview: false,
        handleDateChange: handleDateChange,
        settings: settings,
    })
    fireEvent.click(screen.getAllByLabelText(/Reset this report's settings/)[0])
    expect(handleDateChange).not.toHaveBeenCalled()
})
