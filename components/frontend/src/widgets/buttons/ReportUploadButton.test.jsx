import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { expectFetch, expectNoFetch, expectText } from "../../testUtils"
import * as toast from "../toast"
import { ReportUploadButton } from "./ReportUploadButton"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.resolve({}))
    vi.spyOn(toast, "showMessage")
})

afterEach(() => vi.restoreAllMocks())

function createMockFile(contents) {
    const mockFile = new File([contents], "report.json", { type: "application/json" })
    // File does not have a text method despite the docs saying it should inherit it from Blob. Add it by hand.
    // See https://developer.mozilla.org/en-US/docs/Web/API/File
    mockFile.text = async () => contents
    return mockFile
}

function renderReportUploadButton() {
    const reload = vi.fn()
    render(<ReportUploadButton reload={reload} />)
    return [reload, screen.getByTestId("report-import-input")]
}

it("has the correct label", () => {
    renderReportUploadButton()
    expectText(/Import report/)
})

it("imports a report", async () => {
    const [reload, input] = renderReportUploadButton()
    await userEvent.upload(input, createMockFile("{}"))
    expect(reload).toHaveBeenCalled()
    expectFetch("post", "report/import", {})
    expect(toast.showMessage).not.toHaveBeenCalled()
})

it("cancels importing a report", async () => {
    const [reload, input] = renderReportUploadButton()
    fireEvent.change(input, { target: { files: [] } })
    expect(reload).not.toHaveBeenCalled()
    expectNoFetch()
    expect(toast.showMessage).not.toHaveBeenCalled()
})

it("shows message when failing to import a report", async () => {
    const [reload, input] = renderReportUploadButton()
    await userEvent.upload(input, createMockFile("{]}"))
    expect(reload).not.toHaveBeenCalled()
    expectNoFetch()
    expect(toast.showMessage).toHaveBeenCalledWith(
        "error",
        "Import failed",
        "Expected property name or '}' in JSON at position 1 (line 1 column 2)",
    )
})
