import { ThemeProvider } from "@mui/material/styles"
import { fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { theme } from "../theme"
import { ReportsOverviewDashboard } from "./ReportsOverviewDashboard"

beforeEach(() => {
    mockGetAnimations()
    history.push("")
})

const dataModel = {
    metrics: {
        metric_type: { default_scale: "count" },
    },
}

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            metrics: {
                metric_uuid: { type: "metric_type", tags: ["tag"], recent_measurements: [] },
                another_metric_uuid: {
                    type: "metric_type",
                    tags: ["other"],
                    recent_measurements: [],
                },
            },
        },
    },
    title: "Report",
}

function renderReportsOverviewDashboard({
    dates = [new Date()],
    hiddenTags = null,
    openReport = null,
    reports = [report],
} = {}) {
    let settings = createTestableSettings()
    if (hiddenTags) {
        settings.hiddenTags = hiddenTags
    }
    render(
        <ThemeProvider theme={theme}>
            <DataModel.Provider value={dataModel}>
                <div id="dashboard">
                    <ReportsOverviewDashboard
                        dates={dates}
                        openReport={openReport}
                        reports={reports}
                        settings={settings}
                    />
                </div>
            </DataModel.Provider>
        </ThemeProvider>,
    )
}

it("shows the reports overview dashboard", async () => {
    renderReportsOverviewDashboard()
    expect(screen.getAllByText(/Legend/).length).toBe(1)
})

it("hides tags", async () => {
    history.push("?hidden_tags=other")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    renderReportsOverviewDashboard({ hiddenTags: hiddenTags.result.current })
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.queryAllByText(/other/).length).toBe(0)
})

it("calls the callback on click", async () => {
    const openReport = jest.fn()
    renderReportsOverviewDashboard({ openReport: openReport })
    fireEvent.click(screen.getByText(/Report/))
    expect(openReport).toHaveBeenCalledWith("report_uuid")
})

it("hides the report cards", async () => {
    history.push("?hidden_cards=reports")
    renderReportsOverviewDashboard()
    expect(screen.queryAllByText(/Report/).length).toBe(0)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.getAllByText(/other/).length).toBe(1)
})

it("hides the tag cards", async () => {
    history.push("?hidden_cards=tags")
    renderReportsOverviewDashboard()
    expect(screen.getAllByText(/Report/).length).toBe(1)
    expect(screen.queryAllByText(/tag/).length).toBe(0)
    expect(screen.queryAllByText(/other/).length).toBe(0)
})

it("hides the required actions cards", async () => {
    history.push("?hidden_cards=action_required")
    renderReportsOverviewDashboard()
    expect(screen.getAllByText(/Report/).length).toBe(1)
    expect(screen.queryAllByText(/Action required/).length).toBe(0)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.getAllByText(/other/).length).toBe(1)
})

it("hides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=all")
    renderReportsOverviewDashboard()
    fireEvent.click(screen.getByText(/Action required/))
    expect(history.location.search).toEqual("?metrics_to_hide=no_action_required")
})

it("unhides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderReportsOverviewDashboard()
    fireEvent.click(screen.getByText(/Action required/))
    expect(history.location.search).toEqual("?metrics_to_hide=all")
})

it("hides the legend card", async () => {
    history.push("?hidden_cards=legend")
    renderReportsOverviewDashboard()
    expect(screen.queryAllByText(/Legend/).length).toBe(0)
})
