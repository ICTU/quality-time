import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { expectFetch, expectNoFetch, expectText } from "../../testUtils"
import { SnackbarAlerts } from "../SnackbarAlerts"
import { ReportUploadButton } from "./ReportUploadButton"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi")
})

afterEach(() => vi.restoreAllMocks())

function createMockFile(contents) {
    const mockFile = new File([contents], "report.json", { type: "application/json" })
    // File does not have a text method despite the docs saying it should inherit it from Blob. Add it by hand.
    // See https://developer.mozilla.org/en-US/docs/Web/API/File
    mockFile.text = async () => contents
    return mockFile
}

function renderReportUploadButton({ showMessage = vi.fn() } = {}) {
    const reload = vi.fn()
    render(
        <SnackbarAlerts messages={[]} showMessage={showMessage}>
            <ReportUploadButton reload={reload} />
        </SnackbarAlerts>,
    )
    return [reload, screen.getByTestId("report-import-input")]
}

it("has the correct label", () => {
    renderReportUploadButton()
    expectText(/Import report/)
})

it("imports a report", async () => {
    const showMessage = vi.fn()
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({}) }),
    )
    const [reload, input] = renderReportUploadButton({ showMessage: showMessage })
    await userEvent.upload(input, createMockFile("{}"))
    expect(reload).toHaveBeenCalled()
    expectFetch("post", "report/import", {})
    expect(showMessage).not.toHaveBeenCalled()
})

it("imports a report with warning", async () => {
    const showMessage = vi.fn()
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ ok: true, warning: "Credentials not decrypted" }),
    )
    const [reload, input] = renderReportUploadButton({ showMessage: showMessage })
    await userEvent.upload(input, createMockFile("{}"))
    expect(reload).toHaveBeenCalled()
    expectFetch("post", "report/import", {})
    expect(showMessage).toHaveBeenCalledWith({
        severity: "warning",
        title: "Import warning",
        description: "Credentials not decrypted",
    })
})

it("cancels importing a report", async () => {
    const showMessage = vi.fn()
    const [reload, input] = renderReportUploadButton({ showMessage: showMessage })
    fireEvent.change(input, { target: { files: [] } })
    expect(reload).not.toHaveBeenCalled()
    expectNoFetch()
    expect(showMessage).not.toHaveBeenCalled()
})

it("shows message when failing to parse a report", async () => {
    const showMessage = vi.fn()
    const [reload, input] = renderReportUploadButton({ showMessage: showMessage })
    await userEvent.upload(input, createMockFile("{]}"))
    expect(reload).not.toHaveBeenCalled()
    expectNoFetch()
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Import failed",
        description: "Expected property name or '}' in JSON at position 1 (line 1 column 2)",
    })
})

it("shows message when failing to import a report", async () => {
    const showMessage = vi.fn()
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ ok: false, json: () => Promise.resolve({ error: "Server error message" }) }),
    )
    const [reload, input] = renderReportUploadButton({ showMessage: showMessage })
    await userEvent.upload(input, createMockFile("{}"))
    expect(reload).not.toHaveBeenCalled()
    expectFetch("post", "report/import", {})
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Import failed",
        description: "Server error message",
    })
})
