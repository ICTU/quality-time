import { act, render, screen } from "@testing-library/react"
import history from "history/browser"
import * as react_toastify from "react-toastify"

import { createTestableSettings } from "./__fixtures__/fixtures"
import * as fetch_server_api from "./api/fetch_server_api"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import { PageContent } from "./PageContent"
import { expectNoAccessibilityViolations } from "./testUtils"

jest.mock("react-toastify")
jest.mock("./api/fetch_server_api")

beforeEach(() => {
    jest.useFakeTimers("modern")
    fetch_server_api.api_with_report_date = jest.requireActual("./api/fetch_server_api").api_with_report_date
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve({ ok: true, measurements: [] }))
    mockGetAnimations()
    history.push("")
})

afterEach(() => {
    jest.clearAllMocks()
    jest.useRealTimers()
})

async function renderPageContent({ loading = false, reports = [], report_date = null, report_uuid = "" } = {}) {
    const settings = createTestableSettings()
    let result
    await act(async () => {
        result = render(
            <div id="dashboard">
                <PageContent
                    lastUpdate={new Date()}
                    loading={loading}
                    reports={reports}
                    reports_overview={{}}
                    report_date={report_date}
                    report_uuid={report_uuid}
                    settings={settings}
                />
            </div>,
        )
    })
    return result
}

it("shows the reports overview", async () => {
    const { container } = await renderPageContent({ report_date: new Date(2023, 10, 25) })
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows that the report is missing", async () => {
    const { container } = await renderPageContent({ reports: [{}], report_uuid: "uuid" })
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows that the report was missing", async () => {
    const { container } = await renderPageContent({
        report_date: new Date("2022-03-31"),
        reports: [{}],
        report_uuid: "uuid",
    })
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the loading spinner", async () => {
    const { container } = await renderPageContent({ loading: true })
    expect(screen.getAllByRole("progressbar").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

function expectMeasurementsCall(date, offset = 0) {
    const minReportDate = new Date(date)
    minReportDate.setDate(minReportDate.getDate() - offset)
    minReportDate.setHours(minReportDate.getHours() - 1)
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith(
        "get",
        `measurements?report_date=${date.toISOString()}&min_report_date=${minReportDate.toISOString()}`,
    )
}

it("fetches measurements", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    jest.setSystemTime(mockedDate)
    const { container } = await renderPageContent({ report_date: null })
    expectMeasurementsCall(mockedDate)
    await expectNoAccessibilityViolations(container)
})

it("fetches measurements if nr dates > 1", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    jest.setSystemTime(mockedDate)
    history.push("?date_interval=1&nr_dates=2")
    await renderPageContent()
    expectMeasurementsCall(mockedDate, 1)
})

it("fetches measurements if time traveling", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    jest.setSystemTime(mockedDate)
    const reportDate = new Date(2021, 3, 25)
    await renderPageContent({ report_date: reportDate })
    expectMeasurementsCall(reportDate)
})

it("fetches measurements if nr dates > 1 and time traveling", async () => {
    const mockedDate = new Date("2022-04-27T16:00:05+0000")
    jest.setSystemTime(mockedDate)
    history.push("?date_interval=1&nr_dates=2")
    const reportDate = new Date(2022, 3, 25)
    await renderPageContent({ report_date: reportDate })
    expectMeasurementsCall(reportDate, 1)
})

it("fails to load measurements", async () => {
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.reject(new Error("Error description")))
    await renderPageContent()
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(
        <div>
            <b>Could not fetch measurements</b>
            <p>Error description</p>
        </div>,
    )
})
