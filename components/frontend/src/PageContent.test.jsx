import { act, render, screen } from "@testing-library/react"
import history from "history/browser"
import * as reactToastify from "react-toastify"
import { vi } from "vitest"

import * as fetchServerApi from "./api/fetch_server_api"
import { useSettings } from "./app_ui_settings"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import { PageContent } from "./PageContent"
import { expectFetch, expectNoAccessibilityViolations, expectText } from "./testUtils"

vi.mock("react-toastify")

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

function PageContentWrapper({ lastUpdate, loading, reports, reportDate, reportUuid }) {
    const settings = useSettings(reportUuid)
    return (
        <div id="dashboard">
            <PageContent
                lastUpdate={lastUpdate}
                loading={loading}
                reports={reports}
                reportsOverview={{}}
                reportDate={reportDate}
                reportUuid={reportUuid}
                settings={settings}
            />
        </div>
    )
}

async function renderPageContent({ loading = false, reports = [], reportDate = null, reportUuid = "" } = {}) {
    const lastUpdate = new Date()
    let result
    await act(async () => {
        result = render(
            <PageContentWrapper
                lastUpdate={lastUpdate}
                loading={loading}
                reports={reports}
                reportDate={reportDate}
                reportUuid={reportUuid}
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
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.reject(new Error("Error description")))
    const toast = vi.spyOn(reactToastify, "toast")
    await renderPageContent()
    expect(toast.mock.calls[0][0]).toStrictEqual(
        <div>
            <b>Could not fetch measurements</b>
            <p>Error description</p>
        </div>,
    )
})
