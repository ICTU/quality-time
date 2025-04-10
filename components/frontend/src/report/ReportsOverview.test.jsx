import { ThemeProvider } from "@mui/material/styles"
import { act, fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { expectNoAccessibilityViolations } from "../testUtils"
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
                <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                    <DataModel.Provider value={dataModel}>
                        <ReportsOverview
                            dates={[reportDate || new Date()]}
                            lastUpdate={new Date()}
                            measurements={[{ status: "target_met" }]}
                            reportDate={reportDate}
                            reports={reports}
                            reportsOverview={reportsOverview}
                            settings={settings}
                        />
                    </DataModel.Provider>
                </Permissions.Provider>
            </ThemeProvider>,
        )
    })
    return result
}

it("shows an error message if there are no reports at the specified date", async () => {
    const { container } = await renderReportsOverview({ reportDate: new Date() })
    expect(screen.getAllByText(/Sorry, no reports existed at/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the reports overview", async () => {
    const reports = [{ report_uuid: "report_uuid", subjects: {} }]
    const reportsOverview = { title: "Overview", permissions: {} }
    const { container } = await renderReportsOverview({ reports: reports, reportsOverview: reportsOverview })
    expect(screen.getAllByText(/Overview/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the comment", async () => {
    const reports = [{ report_uuid: "report_uuid", subjects: {} }]
    const reportsOverview = { title: "Overview", comment: "Commentary", permissions: {} }
    const { container } = await renderReportsOverview({ reports: reports, reportsOverview: reportsOverview })
    expect(screen.getAllByText(/Commentary/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
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
    expect(screen.getAllByText(/Foo/).length).toBe(2)
    expect(screen.getAllByText(/Bar/).length).toBe(2)
    fireEvent.click(screen.getAllByText(/Foo/)[0])
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
    expect(screen.getAllByText(/Foo/).length).toBe(2)
    expect(screen.queryAllByText(/Bar/).length).toBe(0)
    fireEvent.click(screen.getAllByText(/Foo/)[0])
    expect(result.current.value).toStrictEqual([])
})

it("adds a report", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true })
    await renderReportsOverview()
    fireEvent.click(screen.getByText(/Add report/))
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "report/new", {})
})

it("copies a report", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true })
    const reports = [{ report_uuid: "uuid", subjects: {}, title: "Existing report" }]
    await renderReportsOverview({ reports: reports })
    fireEvent.click(screen.getByText(/Copy report/))
    await act(async () => {
        fireEvent.click(screen.getAllByRole("menuitem")[1])
    })
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "report/uuid/copy", {})
})
