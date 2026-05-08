import { act, render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { dataModel } from "./__fixtures__/fixtures"
import * as fetchServerApi from "./api/fetch_server_api"
import { useSettings } from "./app_ui_settings"
import { DataModelContext } from "./context/DataModel"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import { PageContent } from "./PageContent"
import { expectFetch, expectNoAccessibilityViolations, expectText } from "./testUtils"
import { SnackbarAlerts } from "./widgets/SnackbarAlerts"

beforeEach(async () => {
    vi.useFakeTimers("modern")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.resolve({ ok: true, measurements: [] }))
    mockGetAnimations()
    history.push("")
})

afterEach(() => {
    vi.clearAllMocks()
    vi.useRealTimers()
})

function PageContentWrapper({ currentReport, lastUpdate, loading, reports, reportDate, reportUuid, showMessage }) {
    const settings = useSettings(reportUuid)
    return (
        <div id="dashboard">
            <DataModelContext value={dataModel}>
                <SnackbarAlerts messages={[]} showMessage={showMessage}>
                    <PageContent
                        currentReport={currentReport}
                        lastUpdate={lastUpdate}
                        loading={loading}
                        reports={reports}
                        reportsOverview={{}}
                        reportDate={reportDate}
                        reportUuid={reportUuid}
                        settings={settings}
                    />
                </SnackbarAlerts>
            </DataModelContext>
        </div>
    )
}

async function renderPageContent({
    currentReport = null,
    loading = false,
    reports = [],
    reportDate = null,
    reportUuid = "",
    showMessage = vi.fn(),
} = {}) {
    const lastUpdate = new Date()
    let result
    await act(async () => {
        result = render(
            <PageContentWrapper
                currentReport={currentReport}
                lastUpdate={lastUpdate}
                loading={loading}
                reports={reports}
                reportDate={reportDate}
                reportUuid={reportUuid}
                showMessage={showMessage}
            />,
        )
    })
    return result
}

it("has no accessibility violations", async () => {
    const { container } = await renderPageContent({ reportDate: new Date(2023, 10, 25) })
    await expectNoAccessibilityViolations(container)
})

it("shows the reports overview", async () => {
    await renderPageContent({ reportDate: new Date(2023, 10, 25) })
    expectText(/Sorry, no reports/)
})

it("shows that the report is missing", async () => {
    await renderPageContent({ reports: [{}], reportUuid: "uuid" })
    expectText(/Sorry, this report doesn't exist/)
})

it("shows that the report was missing", async () => {
    await renderPageContent({
        reportDate: new Date("2022-03-31"),
        reports: [{}],
        reportUuid: "uuid",
    })
    expectText(/Sorry, this report didn't exist/)
})

it("shows the loading spinner", async () => {
    await renderPageContent({ loading: true })
    expect(screen.getAllByRole("progressbar").length).toBe(1)
})

function expectMeasurementsCall(date, offset = 0) {
    const minReportDate = new Date(date)
    minReportDate.setDate(minReportDate.getDate() - offset)
    minReportDate.setHours(minReportDate.getHours() - 1)
    expectFetch("get", `measurements?report_date=${date.toISOString()}&min_report_date=${minReportDate.toISOString()}`)
}

it("fetches measurements", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    vi.setSystemTime(mockedDate)
    await renderPageContent({ reportDate: null })
    expectMeasurementsCall(mockedDate)
})

it("fetches measurements if nr dates > 1", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    vi.setSystemTime(mockedDate)
    history.push("?date_interval=1&nr_dates=2")
    await renderPageContent()
    expectMeasurementsCall(mockedDate, 1)
})

it("fetches measurements if time traveling", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    vi.setSystemTime(mockedDate)
    const reportDate = new Date(2021, 3, 25)
    await renderPageContent({ reportDate: reportDate })
    expectMeasurementsCall(reportDate)
})

it("fetches measurements if nr dates > 1 and time traveling", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    vi.setSystemTime(mockedDate)
    history.push("?date_interval=1&nr_dates=2")
    const reportDate = new Date(2022, 3, 25)
    await renderPageContent({ reportDate: reportDate })
    expectMeasurementsCall(reportDate, 1)
})

it("fails to load measurements", async () => {
    const showMessage = vi.fn()
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.reject(new Error("Error description")))
    await renderPageContent({ showMessage: showMessage })
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Could not fetch measurements",
        description: "Error description",
    })
})

it("uses ascending date order when configured", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    vi.setSystemTime(mockedDate)
    history.push("?date_interval=1&nr_dates=2&date_order=ascending")
    await renderPageContent()
    expectMeasurementsCall(mockedDate, 1)
})

it("treats a measurement response without a measurements field as empty", async () => {
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.resolve({ ok: true }))
    const report = { report_uuid: "uuid", title: "Report title", subjects: {} }
    await renderPageContent({ currentReport: report, reports: [report], reportUuid: "uuid" })
    // Without the `?? []` fallback, Report.jsx's `measurements.slice()` would throw
    expectText(/Report title/, 2)
})
