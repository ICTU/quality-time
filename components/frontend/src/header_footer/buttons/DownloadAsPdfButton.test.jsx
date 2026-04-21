import { render, screen, waitFor } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { asyncClickText, expectFetch, expectLabelText, expectNoAccessibilityViolations } from "../../testUtils"
import { SnackbarAlerts } from "../../widgets/SnackbarAlerts"
import { DownloadAsPdfButton } from "./DownloadAsPdfButton"

beforeEach(() => {
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.resolve({ ok: true }))
})

function renderDownloadAsPdfButton(props) {
    return render(
        <SnackbarAlerts messages={[]} showMessage={props?.showMessage ?? vi.fn()}>
            <DownloadAsPdfButton {...props} />
        </SnackbarAlerts>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderDownloadAsPdfButton()
    await expectNoAccessibilityViolations(container)
})

test("DownloadAsPdfButton has the correct label for reports overview", () => {
    renderDownloadAsPdfButton()
    expectLabelText(/Generate a PDF version/, 2) // 2 due to 10840-menubar-color-contrast-for-disabled-items
})

test("DownloadAsPdfButton has the correct label for a report", () => {
    renderDownloadAsPdfButton({ reportUuid: "report_uuid" })
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
        return new Promise((resolve) => setTimeout(resolve, 100))
    })
}

test("DownloadAsPdfButton indicates loading on click", async () => {
    const showMessage = vi.fn()
    mockGetReportPdfWithTimeout()
    renderDownloadAsPdfButton({ reportUuid: "report_uuid", showMessage: showMessage })
    await clickDownload()
    expectButtonIsLoading()
    expectFetch(
        "get",
        "report/report_uuid/pdf?language=en-US&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Flanguage%3Den-US",
        {},
        "application/pdf",
    )
    await waitFor(() => {
        expect(showMessage).toHaveBeenCalledTimes(1)
    })
})

test("DownloadAsPdfButton ignores a second click", async () => {
    const showMessage = vi.fn()
    mockGetReportPdfWithTimeout()
    renderDownloadAsPdfButton({ reportUuid: "report_uuid", showMessage: showMessage })
    await clickDownload(2)
    expectButtonIsLoading()
    expectFetch(
        "get",
        "report/report_uuid/pdf?language=en-US&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Flanguage%3Den-US",
        {},
        "application/pdf",
    )
    await waitFor(() => {
        expect(showMessage).toHaveBeenCalledTimes(1)
    })
})

test("DownloadAsPdfButton ignores unregistered query parameters", async () => {
    history.push("?unregister_key=value&nr_dates=4")
    renderDownloadAsPdfButton({ reportUuid: "report_uuid" })
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
    renderDownloadAsPdfButton({ reportUuid: "report_uuid" })
    await clickDownload()
    expectFetch(
        "get",
        "report/report_uuid/pdf?language=nl-NL&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Flanguage%3Dnl-NL",
        {},
        "application/pdf",
    )
})

test("DownloadAsPdfButton stops loading after returning pdf", async () => {
    const showMessage = vi.fn()
    HTMLAnchorElement.prototype.click = vi.fn() // Prevent "Not implemented: navigation (except hash changes)"
    globalThis.URL.createObjectURL = vi.fn()
    renderDownloadAsPdfButton({ showMessage: showMessage })
    await clickDownload()
    expectButtonIsNotLoading()
    expect(showMessage).toHaveBeenCalledTimes(0)
})

test("DownloadAsPdfButton stops loading after receiving error", async () => {
    const showMessage = vi.fn()
    fetchServerApi.fetchServerApi.mockImplementation(() =>
        Promise.resolve({ ok: false, status: "403", statusText: "access denied" }),
    )
    renderDownloadAsPdfButton({ showMessage: showMessage })
    await clickDownload()
    expectButtonIsNotLoading()
    expect(showMessage).toHaveBeenCalledTimes(1)
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "PDF rendering failed",
        description: "HTTP code 403: access denied",
    })
})

test("DownloadAsPdfButton catches errors", async () => {
    const showMessage = vi.fn()
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.reject(new Error("Oops")))
    renderDownloadAsPdfButton({ showMessage: showMessage })
    await clickDownload()
    expectButtonIsNotLoading()
    expect(showMessage).toHaveBeenCalledTimes(1)
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Could not fetch PDF report",
        description: "Error: Oops",
    })
})
