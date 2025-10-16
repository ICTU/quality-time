import { render, screen, waitFor } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { asyncClickText, expectFetch, expectLabelText } from "../../testUtils"
import * as toast from "../../widgets/toast"
import { DownloadAsPdfButton } from "./DownloadAsPdfButton"

beforeEach(() => {
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.resolve({ ok: true }))
    vi.spyOn(toast, "showMessage")
})

test("DownloadAsPdfButton has the correct label for reports overview", () => {
    render(<DownloadAsPdfButton />)
    expectLabelText(/Generate a PDF version/, 2) // 2 due to 10840-menubar-color-contrast-for-disabled-items
})

test("DownloadAsPdfButton has the correct label for a report", () => {
    render(<DownloadAsPdfButton reportUuid={"report_uuid"} />)
    expectLabelText(/Generate a PDF version/, 2) // 2 due to 10840-menubar-color-contrast-for-disabled-items
})

async function clickDownload(nrClicks = 1) {
    for (let step = 0; step < nrClicks; step++) {
        await asyncClickText(/Download as PDF/)
    }
}

function expectButtonIsLoading() {
    expect(screen.getByRole("button").className).toContain("MuiButton-loading")
}

function expectButtonIsNotLoading() {
    expect(screen.getByRole("button").className).not.toContain("MuiButton-loading")
}

function mockGetReportPdfWithTimeout() {
    fetchServerApi.fetchServerApi.mockImplementation(() => {
        // See https://github.com/eslint-community/eslint-plugin-promise/issues/111#issuecomment-663824152
        return new Promise((resolve) => setTimeout(resolve, 100)) // eslint-disable-line promise/avoid-new
    })
}

test("DownloadAsPdfButton indicates loading on click", async () => {
    mockGetReportPdfWithTimeout()
    render(<DownloadAsPdfButton reportUuid="report_uuid" />)
    await clickDownload()
    expectButtonIsLoading()
    expectFetch(
        "get",
        "report/report_uuid/pdf?language=en-US&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Flanguage%3Den-US",
        {},
        "application/pdf",
    )
    await waitFor(() => {
        expect(toast.showMessage).toHaveBeenCalledTimes(1)
    })
})

test("DownloadAsPdfButton ignores a second click", async () => {
    mockGetReportPdfWithTimeout()
    render(<DownloadAsPdfButton reportUuid="report_uuid" />)
    await clickDownload(2)
    expectButtonIsLoading()
    expectFetch(
        "get",
        "report/report_uuid/pdf?language=en-US&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Flanguage%3Den-US",
        {},
        "application/pdf",
    )
    await waitFor(() => {
        expect(toast.showMessage).toHaveBeenCalledTimes(1)
    })
})

test("DownloadAsPdfButton ignores unregistered query parameters", async () => {
    history.push("?unregister_key=value&nr_dates=4")
    render(<DownloadAsPdfButton reportUuid="report_uuid" />)
    await clickDownload()
    expectFetch(
        "get",
        "report/report_uuid/pdf?nr_dates=4&language=en-US&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Fnr_dates%3D4%26language%3Den-US",
        {},
        "application/pdf",
    )
})

test("DownloadAsPdfButton passes the language set in the user's browser", async () => {
    vi.spyOn(navigator, "language", "get").mockImplementation(() => "nl-NL")
    render(<DownloadAsPdfButton reportUuid="report_uuid" />)
    await clickDownload()
    expectFetch(
        "get",
        "report/report_uuid/pdf?language=nl-NL&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Flanguage%3Dnl-NL",
        {},
        "application/pdf",
    )
})

test("DownloadAsPdfButton stops loading after returning pdf", async () => {
    HTMLAnchorElement.prototype.click = vi.fn() // Prevent "Not implemented: navigation (except hash changes)"
    globalThis.URL.createObjectURL = vi.fn()
    render(<DownloadAsPdfButton />)
    await clickDownload()
    expectButtonIsNotLoading()
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
})

test("DownloadAsPdfButton stops loading after receiving error", async () => {
    fetchServerApi.fetchServerApi.mockImplementation(() =>
        Promise.resolve({ ok: false, status: "403", statusText: "access denied" }),
    )
    render(<DownloadAsPdfButton />)
    await clickDownload()
    expectButtonIsNotLoading()
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "PDF rendering failed", "HTTP code 403: access denied")
})

test("DownloadAsPdfButton catches errors", async () => {
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.reject(new Error("Oops")))
    render(<DownloadAsPdfButton />)
    await clickDownload()
    expectButtonIsNotLoading()
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not fetch PDF report", "Error: Oops")
})
