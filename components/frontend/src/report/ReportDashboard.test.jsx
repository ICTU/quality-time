import { ThemeProvider } from "@mui/material/styles"
import { render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { clickText, expectNoAccessibilityViolations, expectNoText, expectSearch, expectText } from "../testUtils"
import { theme } from "../theme"
import { ReportDashboard } from "./ReportDashboard"

let report

beforeEach(() => {
    mockGetAnimations()
    history.push("")
    report = {
        report_uuid: "report_uuid",
        subjects: {
            subject_uuid: {
                name: "Subject title",
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
    }
})

const dataModel = {
    metrics: {
        metric_type: { default_scale: "count" },
    },
}

function DashboardWrapper({ dates, onClick, reportToRender }) {
    const settings = useSettings()
    return (
        <ThemeProvider theme={theme}>
            <DataModelContext value={dataModel}>
                <div id="dashboard">
                    <ReportDashboard dates={dates} onClick={onClick} report={reportToRender} settings={settings} />
                </div>
            </DataModelContext>
        </ThemeProvider>
    )
}

function renderDashboard({ dates = [new Date()], onClick = vi.fn(), reportToRender = null } = {}) {
    return render(<DashboardWrapper dates={dates} onClick={onClick} reportToRender={reportToRender} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderDashboard({ reportToRender: report })
    await expectNoAccessibilityViolations(container)
})

it("shows the dashboard", async () => {
    renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectText(/Legend/)
    expectText(/tag/)
    expectText(/other/)
})

it("hides tags", async () => {
    history.push("?hidden_tags=other")
    renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectText(/tag/)
    expectNoText(/other/)
})

it("hides a subject if all its tags are hidden", async () => {
    history.push("?hidden_tags=other,tag")
    renderDashboard({ reportToRender: report })
    expectNoText(/Subject title/)
    expectNoText(/tag/)
    expectNoText(/other/)
})

it("expands the subject title on click", async () => {
    const onClick = vi.fn()
    renderDashboard({ reportToRender: report, onClick: onClick })
    clickText(/Subject title/)
    expect(onClick).toHaveBeenCalledWith(expect.anything(), "subject_uuid")
})

it("hides the subject cards", async () => {
    history.push("?hidden_cards=subjects")
    renderDashboard({ reportToRender: report })
    expectNoText(/Subject title/)
    expectText(/Action required/)
    expectText(/tag/)
    expectText(/other/)
})

it("hides the tag cards", async () => {
    history.push("?hidden_cards=tags")
    renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectText(/Action required/)
    expectNoText(/tag/)
    expectNoText(/other/)
})

it("hides the required actions cards", async () => {
    history.push("?hidden_cards=action_required")
    renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectNoText(/Action required/)
    expectText(/tag/)
    expectText(/other/)
})

it("hides metrics not requiring action", async () => {
    renderDashboard({ reportToRender: report })
    clickText(/Action required/)
    expectSearch("?metrics_to_hide=no_action_required")
})

it("unhides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderDashboard({ reportToRender: report })
    clickText(/Action required/)
    expectSearch("")
})

it("hides the legend card", async () => {
    history.push("?hidden_cards=legend")
    renderDashboard({ reportToRender: report })
    expectNoText(/Legend/)
})

it("does not show the issues card without issue tracker", async () => {
    renderDashboard({ reportToRender: report })
    expectNoText(/Issues/)
})

it("does show the issues card with issue tracker", async () => {
    report["issue_tracker"] = { type: "jira" }
    renderDashboard({ reportToRender: report })
    expectText(/Issues/)
})

it("hides the issues card", async () => {
    history.push("?hidden_cards=issues")
    report["issue_tracker"] = { type: "jira" }
    renderDashboard({ reportToRender: report })
    expectNoText(/Issues/)
})

it("hides metrics without issues", async () => {
    report["issue_tracker"] = { type: "jira" }
    renderDashboard({ reportToRender: report })
    clickText(/Issues/)
    expectSearch("?metrics_to_hide=no_issues")
})

it("unhides metrics without issues", async () => {
    report["issue_tracker"] = { type: "jira" }
    history.push("?metrics_to_hide=no_issues")
    renderDashboard({ reportToRender: report })
    clickText(/Issues/)
    expectSearch("")
})
