import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { expectFetch, expectText } from "../../testUtils"
import * as toast from "../toast"
import { ExportReportButton } from "./ExportReportButton"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ report_uuid: "uuid", title: "Report" }),
    )
    vi.spyOn(toast, "showMessage")
    globalThis.URL.createObjectURL = vi.fn(() => "#dummy")
})

afterEach(() => vi.restoreAllMocks())

function renderExportReportButton() {
    render(<ExportReportButton reportUuid="report_uuid" />)
}

it("has the correct label", () => {
    renderExportReportButton()
    expectText(/Export report/)
})

it("exports a report", async () => {
    renderExportReportButton()
    await userEvent.click(screen.getByText(/Export report/))
    expectFetch("get", "report/report_uuid/json")
    expect(toast.showMessage).not.toHaveBeenCalled()
})

it("shows message when export fails", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ ok: false, status: 500, statusText: "Internal Server Error" }),
    )
    renderExportReportButton()
    await userEvent.click(screen.getByText(/Export report/))
    expectFetch("get", "report/report_uuid/json")
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Export failed", "HTTP code 500: Internal Server Error")
})

it("shows message when fetch throws", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.reject(new Error("Network error")))
    renderExportReportButton()
    await userEvent.click(screen.getByText(/Export report/))
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not export report", "Error: Network error")
})
