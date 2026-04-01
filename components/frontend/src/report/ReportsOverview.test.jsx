import { ThemeProvider } from "@mui/material/styles"
import { act, render, renderHook } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import {
    asyncClickMenuItem,
    clickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectNoText,
    expectText,
} from "../testUtils"
import { theme } from "../theme"
import { ReportsOverview } from "./ReportsOverview"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockReturnValue({ then: vi.fn().mockReturnValue({ finally: vi.fn() }) })
    mockGetAnimations()
    history.push("")
})

afterEach(() => vi.restoreAllMocks())

async function renderReportsOverview({
    hiddenTags = null,
    reportDate = null,
    reports = [],
    reportsOverview = {},
} = {}) {
    let settings = createTestableSettings()
    if (hiddenTags) {
        settings.hiddenTags = hiddenTags
    }
    let result
    await act(async () => {
        result = render(
            <ThemeProvider theme={theme}>
                <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                    <DataModelContext value={dataModel}>
                        <ReportsOverview
                            dates={[reportDate || new Date()]}
                            lastUpdate={new Date()}
                            measurements={[{ status: "target_met" }]}
                            reportDate={reportDate}
                            reports={reports}
                            reportsOverview={reportsOverview}
                            settings={settings}
                        />
                    </DataModelContext>
                </PermissionsContext>
            </ThemeProvider>,
        )
    })
    return result
}

it("has no accessibility violations", async () => {
    const { container } = await renderReportsOverview()
    await expectNoAccessibilityViolations(container)
})

it("shows an error message if there are no reports at the specified date", async () => {
    await renderReportsOverview({ reportDate: new Date() })
    expectText(/Sorry, no reports existed at/)
})

it("shows the reports overview", async () => {
    const reports = [{ report_uuid: "report_uuid", subjects: {} }]
    const reportsOverview = { title: "Overview", permissions: {} }
    await renderReportsOverview({ reports: reports, reportsOverview: reportsOverview })
    expectText(/Overview/)
})

it("shows the comment", async () => {
    const reports = [{ report_uuid: "report_uuid", subjects: {} }]
    const reportsOverview = { title: "Overview", comment: "Commentary", permissions: {} }
    await renderReportsOverview({ reports: reports, reportsOverview: reportsOverview })
    expectText(/Commentary/)
})

const reports = [
    {
        report_uuid: "report_uuid",
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        recent_measurements: [],
                        tags: ["Foo"],
                        type: "metric_type",
                    },
                    metric_uuid2: {
                        recent_measurements: [],
                        tags: ["Bar"],
                        type: "metric_type",
                    },
                },
                type: "subject_type",
            },
        },
    },
]

const reportsOverview = { title: "Overview", permissions: {} }

it("hides the report tag cards", async () => {
    const { result } = renderHook(() => useHiddenTagsURLSearchQuery())
    await renderReportsOverview({
        reports: reports,
        reportsOverview: reportsOverview,
        hiddenTags: result.current,
    })
    expectText(/Foo/, 2)
    expectText(/Bar/, 2)
    clickText(/Foo/, 0)
    expect(result.current.value).toStrictEqual(["Bar"])
})

it("shows the report tag cards", async () => {
    history.push("?hidden_tags=Bar")
    const { result } = renderHook(() => useHiddenTagsURLSearchQuery())
    await renderReportsOverview({
        reports: reports,
        reportsOverview: reportsOverview,
        hiddenTags: result.current,
    })
    expectText(/Foo/, 2)
    expectNoText(/Bar/)
    clickText(/Foo/, 0)
    expect(result.current.value).toStrictEqual([])
})

it("adds a report", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true })
    await renderReportsOverview()
    clickText(/Add report/)
    expectFetch("post", "report/new", {})
})

it("copies a report", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true })
    const reports = [{ report_uuid: "uuid", subjects: {}, title: "Existing report" }]
    await renderReportsOverview({ reports: reports })
    clickText(/Copy report/)
    asyncClickMenuItem(undefined, 1)
    expectFetch("post", "report/uuid/copy", {})
})
