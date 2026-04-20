import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { expectFetch, expectText } from "../../testUtils"
import { SnackbarAlerts } from "../SnackbarAlerts"
import { ExportReportButton } from "./ExportReportButton"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ report_uuid: "uuid", title: "Report" }),
    )
    globalThis.URL.createObjectURL = vi.fn(() => "#dummy")
})

afterEach(() => vi.restoreAllMocks())

function renderExportReportButton({ showMessage = vi.fn() } = {}) {
    render(
        <SnackbarAlerts messages={[]} showMessage={showMessage}>
            <ExportReportButton reportUuid="report_uuid" />
        </SnackbarAlerts>,
    )
}

it("has the correct label", () => {
    renderExportReportButton()
    expectText(/Export report/)
})

it("exports a report", async () => {
    const showMessage = vi.fn()
    renderExportReportButton({ showMessage: showMessage })
    await userEvent.click(screen.getByText(/Export report/))
    expectFetch("get", "report/report_uuid/json")
    expect(showMessage).not.toHaveBeenCalled()
})

it("shows message when export fails", async () => {
    const showMessage = vi.fn()
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ ok: false, status: 500, statusText: "Internal Server Error" }),
    )
    renderExportReportButton({ showMessage: showMessage })
    await userEvent.click(screen.getByText(/Export report/))
    expectFetch("get", "report/report_uuid/json")
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Export failed",
        description: "HTTP code 500: Internal Server Error",
    })
})

it("shows message when fetch throws", async () => {
    const showMessage = vi.fn()
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.reject(new Error("Network error")))
    renderExportReportButton({ showMessage: showMessage })
    await userEvent.click(screen.getByText(/Export report/))
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Could not export report",
        description: "Error: Network error",
    })
})
