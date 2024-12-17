import { act, fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings, dataModel } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { ReportsOverview } from "./ReportsOverview"

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) })
    mockGetAnimations()
    history.push("")
})

afterEach(() => jest.restoreAllMocks())

function renderReportsOverview({ hiddenTags = null, reportDate = null, reports = [], reportsOverview = {} } = {}) {
    let settings = createTestableSettings()
    if (hiddenTags) {
        settings.hiddenTags = hiddenTags
    }
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <ReportsOverview
                    dates={[reportDate || new Date()]}
                    lastUpdate={new Date()}
                    measurements={[{ status: "target_met" }]}
                    report_date={reportDate}
                    reports={reports}
                    reports_overview={reportsOverview}
                    settings={settings}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("shows an error message if there are no reports at the specified date", async () => {
    renderReportsOverview({ reportDate: new Date() })
    expect(screen.getAllByText(/Sorry, no reports existed at/).length).toBe(1)
})

it("shows the reports overview", async () => {
    const reports = [{ report_uuid: "report_uuid", subjects: {} }]
    const reportsOverview = { title: "Overview", permissions: {} }
    renderReportsOverview({ reports: reports, reportsOverview: reportsOverview })
    expect(screen.getAllByText(/Overview/).length).toBe(2)
})

it("shows the comment", async () => {
    const reports = [{ report_uuid: "report_uuid", subjects: {} }]
    const reportsOverview = { title: "Overview", comment: "Commentary", permissions: {} }
    renderReportsOverview({ reports: reports, reportsOverview: reportsOverview })
    expect(screen.getAllByText(/Commentary/).length).toBe(1)
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
    renderReportsOverview({
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
    renderReportsOverview({
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
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderReportsOverview()
    fireEvent.click(screen.getByText(/Add report/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/new", {})
})

it("copies a report", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    const reports = [{ report_uuid: "uuid", subjects: {}, title: "Existing report" }]
    renderReportsOverview({ reports: reports })
    fireEvent.click(screen.getByText(/Copy report/))
    await act(async () => {
        fireEvent.click(screen.getAllByRole("menuitem")[1])
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/uuid/copy", {})
})
