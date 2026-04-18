import { render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { useSettings } from "../../app_ui_settings"
import { clickText, expectNoAccessibilityViolations, expectSearch } from "../../testUtils"
import { ResetSettingsButton } from "./ResetSettingsButton"

beforeEach(() => {
    history.push("")
})

function ResetSettingsButtonWrapper({ atReportsOverview, handleDateChange, reportDate }) {
    const settings = useSettings()
    return (
        <ResetSettingsButton
            atReportsOverview={atReportsOverview}
            handleDateChange={handleDateChange}
            reportDate={reportDate}
            settings={settings}
        />
    )
}

function renderResetSettingsButton({ atReportsOverview = true, handleDateChange = vi.fn(), reportDate = null } = {}) {
    return render(
        <ResetSettingsButtonWrapper
            atReportsOverview={atReportsOverview}
            handleDateChange={handleDateChange}
            reportDate={reportDate}
        />,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderResetSettingsButton()
    await expectNoAccessibilityViolations(container)
})

it("resets the settings", async () => {
    history.push(
        "?date_interval=2&date_order=ascending&entity_sort_column=metric_uuid:status&" +
            "entity_sort_direction=metric_uuid:descending&hidden_columns=comment&" +
            "hide_ignored_entities=metric_uuid&hidden_tags=tag&metrics_to_hide=no_action_required&nr_dates=2&" +
            "show_issue_creation_date=true&show_issue_summary=true&show_issue_update_date=true&" +
            "show_issue_due_date=true&show_issue_release=true&show_issue_sprint=true&sort_column=status&" +
            "sort_direction=descending&expanded=tab:0&hidden_cards=tags",
    )
    const handleDateChange = vi.fn()
    renderResetSettingsButton({ handleDateChange: handleDateChange, reportDate: new Date("2023-01-01") })
    clickText(/Reset settings/, 0)
    expectSearch("")
    expect(handleDateChange).toHaveBeenCalledWith(null)
})

it("does not reset the settings when all have the default value", async () => {
    const handleDateChange = vi.fn()
    renderResetSettingsButton({ atReportsOverview: false, handleDateChange: handleDateChange })
    clickText(/Reset settings/, 0)
    expect(handleDateChange).not.toHaveBeenCalled()
})
