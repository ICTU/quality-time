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

function renderDashboard({ hiddenTags = null, dates = [new Date()], onClick = vi.fn(), reportToRender = null } = {}) {
    let settings = createTestableSettings()
    if (hiddenTags) {
        settings.hiddenTags = hiddenTags
    }
    return render(
        <ThemeProvider theme={theme}>
            <DataModel.Provider value={dataModel}>
                <div id="dashboard">
                    <ReportDashboard dates={dates} onClick={onClick} report={reportToRender} settings={settings} />
                </div>
            </DataModel.Provider>
        </ThemeProvider>,
    )
}

it("shows the dashboard", async () => {
    const { container } = renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectText(/Legend/)
    expectText(/tag/)
    expectText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides tags", async () => {
    history.push("?hidden_tags=other")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    const { container } = renderDashboard({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    expectText(/Subject title/)
    expectText(/tag/)
    expectNoText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides a subject if all its tags are hidden", async () => {
    history.push("?hidden_tags=other,tag")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    const { container } = renderDashboard({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    expectNoText(/Subject title/)
    expectNoText(/tag/)
    expectNoText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("expands the subject title on click", async () => {
    const onClick = vi.fn()
    const { container } = renderDashboard({ reportToRender: report, onClick: onClick })
    clickText(/Subject title/)
    expect(onClick).toHaveBeenCalledWith(expect.anything(), "subject_uuid")
    await expectNoAccessibilityViolations(container)
})

it("hides the subject cards", async () => {
    history.push("?hidden_cards=subjects")
    const { container } = renderDashboard({ reportToRender: report })
    expectNoText(/Subject title/)
    expectText(/Action required/)
    expectText(/tag/)
    expectText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides the tag cards", async () => {
    history.push("?hidden_cards=tags")
    const { container } = renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectText(/Action required/)
    expectNoText(/tag/)
    expectNoText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides the required actions cards", async () => {
    history.push("?hidden_cards=action_required")
    const { container } = renderDashboard({ reportToRender: report })
    expectText(/Subject title/)
    expectNoText(/Action required/)
    expectText(/tag/)
    expectText(/other/)
    await expectNoAccessibilityViolations(container)
})

it("hides metrics not requiring action", async () => {
    const { container } = renderDashboard({ reportToRender: report })
    clickText(/Action required/)
    expectSearch("?metrics_to_hide=no_action_required")
    await expectNoAccessibilityViolations(container)
})

it("unhides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=no_action_required")
    const { container } = renderDashboard({ reportToRender: report })
    clickText(/Action required/)
    expectSearch("")
    await expectNoAccessibilityViolations(container)
})

it("hides the legend card", async () => {
    history.push("?hidden_cards=legend")
    const { container } = renderDashboard({ reportToRender: report })
    expectNoText(/Legend/)
    await expectNoAccessibilityViolations(container)
})

it("does not show the issues card without issue tracker", async () => {
    const { container } = renderDashboard({ reportToRender: report })
    expectNoText(/Issues/)
    await expectNoAccessibilityViolations(container)
})

it("does show the issues card with issue tracker", async () => {
    report["issue_tracker"] = { type: "jira" }
    const { container } = renderDashboard({ reportToRender: report })
    expectText(/Issues/)
    await expectNoAccessibilityViolations(container)
})

it("hides the issues card", async () => {
    history.push("?hidden_cards=issues")
    report["issue_tracker"] = { type: "jira" }
    const { container } = renderDashboard({ reportToRender: report })
    expectNoText(/Issues/)
    await expectNoAccessibilityViolations(container)
})

it("hides metrics without issues", async () => {
    report["issue_tracker"] = { type: "jira" }
    const { container } = renderDashboard({ reportToRender: report })
    clickText(/Issues/)
    expectSearch("?metrics_to_hide=no_issues")
    await expectNoAccessibilityViolations(container)
})

it("unhides metrics without issues", async () => {
    report["issue_tracker"] = { type: "jira" }
    history.push("?metrics_to_hide=no_issues")
    const { container } = renderDashboard({ reportToRender: report })
    clickText(/Issues/)
    expectSearch("")
    await expectNoAccessibilityViolations(container)
})
