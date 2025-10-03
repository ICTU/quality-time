import { ThemeProvider } from "@mui/material/styles"
import { render, renderHook } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { clickText, expectNoAccessibilityViolations, expectNoText, expectSearch, expectText } from "../testUtils"
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
    return render(
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
    const { container } = renderReportsOverviewDashboard()
    expectText(/Legend/)
    await expectNoAccessibilityViolations(container)
})

it("hides tags", async () => {
    history.push("?hidden_tags=other")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    const { container } = renderReportsOverviewDashboard({ hiddenTags: hiddenTags.result.current })
    expectText(/tag/)
    expectNoText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("calls the callback on click", async () => {
    const openReport = vi.fn()
    const { container } = renderReportsOverviewDashboard({ openReport: openReport })
    clickText(/Report/)
    expect(openReport).toHaveBeenCalledWith("report_uuid")
    await expectNoAccessibilityViolations(container)
})

it("hides the report cards", async () => {
    history.push("?hidden_cards=reports")
    const { container } = renderReportsOverviewDashboard()
    expectNoText(/Report/)
    expectText(/tag/)
    expectText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides the tag cards", async () => {
    history.push("?hidden_cards=tags")
    const { container } = renderReportsOverviewDashboard()
    expectText(/Report/)
    expectNoText(/tag/)
    expectNoText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides the required actions cards", async () => {
    history.push("?hidden_cards=action_required")
    const { container } = renderReportsOverviewDashboard()
    expectText(/Report/)
    expectNoText(/Action required/)
    expectText(/tag/)
    expectText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=all")
    const { container } = renderReportsOverviewDashboard()
    clickText(/Action required/)
    expectSearch("?metrics_to_hide=no_action_required")
    await expectNoAccessibilityViolations(container)
})

it("unhides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=no_action_required")
    const { container } = renderReportsOverviewDashboard()
    clickText(/Action required/)
    expectSearch("?metrics_to_hide=all")
    await expectNoAccessibilityViolations(container)
})

it("hides the legend card", async () => {
    history.push("?hidden_cards=legend")
    const { container } = renderReportsOverviewDashboard()
    expectNoText(/Legend/)
    await expectNoAccessibilityViolations(container)
})
