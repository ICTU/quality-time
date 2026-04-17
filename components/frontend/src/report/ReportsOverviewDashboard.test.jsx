import { ThemeProvider } from "@mui/material/styles"
import { render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
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

function ReportsOverviewDashboardWrapper({ dates, openReport, reports }) {
    const settings = useSettings()
    return (
        <ThemeProvider theme={theme}>
            <DataModelContext value={dataModel}>
                <div id="dashboard">
                    <ReportsOverviewDashboard
                        dates={dates}
                        openReport={openReport}
                        reports={reports}
                        settings={settings}
                    />
                </div>
            </DataModelContext>
        </ThemeProvider>
    )
}

function renderReportsOverviewDashboard({ openReport = null, reports = [report] } = {}) {
    return render(<ReportsOverviewDashboardWrapper dates={[new Date()]} openReport={openReport} reports={reports} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderReportsOverviewDashboard()
    await expectNoAccessibilityViolations(container)
})

it("shows the reports overview dashboard", async () => {
    renderReportsOverviewDashboard()
    expectText(/Legend/)
})

it("hides tags", async () => {
    history.push("?hidden_tags=other")
    renderReportsOverviewDashboard()
    expectText(/tag/)
    expectNoText(/other/)
})

it("calls the callback on click", async () => {
    const openReport = vi.fn()
    renderReportsOverviewDashboard({ openReport: openReport })
    clickText(/Report/)
    expect(openReport).toHaveBeenCalledWith("report_uuid")
})

it("hides the report cards", async () => {
    history.push("?hidden_cards=reports")
    renderReportsOverviewDashboard()
    expectNoText(/Report/)
    expectText(/tag/)
    expectText(/other/)
})

it("hides the tag cards", async () => {
    history.push("?hidden_cards=tags")
    renderReportsOverviewDashboard()
    expectText(/Report/)
    expectNoText(/tag/)
    expectNoText(/other/)
})

it("hides the required actions cards", async () => {
    history.push("?hidden_cards=action_required")
    renderReportsOverviewDashboard()
    expectText(/Report/)
    expectNoText(/Action required/)
    expectText(/tag/)
    expectText(/other/)
})

it("hides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=all")
    renderReportsOverviewDashboard()
    clickText(/Action required/)
    expectSearch("?metrics_to_hide=no_action_required")
})

it("unhides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderReportsOverviewDashboard()
    clickText(/Action required/)
    expectSearch("?metrics_to_hide=all")
})

it("hides the legend card", async () => {
    history.push("?hidden_cards=legend")
    renderReportsOverviewDashboard()
    expectNoText(/Legend/)
})
