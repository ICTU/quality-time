import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import * as get_report_pdf from "../../api/report"
import * as toast from "../../widgets/toast"
import { DownloadAsPDFButton } from "./DownloadAsPDFButton"

vi.mock("../../api/report")
vi.mock("../../widgets/toast.jsx")

beforeEach(() => {
    vi.resetAllMocks()
    get_report_pdf.get_report_pdf.mockImplementation(() => Promise.resolve({ ok: true }))
})

test("DownloadAsPDFButton has the correct label for reports overview", () => {
    render(<DownloadAsPDFButton />)
    expect(screen.getAllByLabelText(/reports overview as PDF/).length).toBe(1)
})

test("DownloadAsPDFButton has the correct label for a report", () => {
    render(<DownloadAsPDFButton report_uuid={"report_uuid"} />)
    expect(screen.getAllByLabelText(/report as PDF/).length).toBe(1)
})

async function clickDownload(nrClicks = 1) {
    for (let step = 0; step < nrClicks; step++) {
        await act(async () => {
            fireEvent.click(screen.getByText(/Download as PDF/))
        })
    }
}

function expectButtonIsLoading() {
    expect(screen.getByRole("button").className).toContain("MuiButton-loading")
}

function expectButtonIsNotLoading() {
    expect(screen.getByRole("button").className).not.toContain("MuiButton-loading")
}

function mockGetReportPDFWithTimeout() {
    get_report_pdf.get_report_pdf.mockImplementation(() => {
        // See https://github.com/eslint-community/eslint-plugin-promise/issues/111#issuecomment-663824152
        return new Promise((resolve) => setTimeout(resolve, 100)) // eslint-disable-line promise/avoid-new
    })
}

test("DownloadAsPDFButton indicates loading on click", async () => {
    mockGetReportPDFWithTimeout()
    render(<DownloadAsPDFButton report_uuid="report_uuid" />)
    await clickDownload()
    expectButtonIsLoading()
    expect(get_report_pdf.get_report_pdf).toHaveBeenCalledWith(
        "report_uuid",
        "?report_url=http%3A%2F%2Flocalhost%3A3000%2F",
    )
    await waitFor(() => {
        expect(toast.showMessage).toHaveBeenCalledTimes(1)
    })
})

test("DownloadAsPDFButton ignores a second click", async () => {
    mockGetReportPDFWithTimeout()
    render(<DownloadAsPDFButton report_uuid="report_uuid" />)
    await clickDownload(2)
    expectButtonIsLoading()
    expect(get_report_pdf.get_report_pdf).toHaveBeenCalledWith(
        "report_uuid",
        "?report_url=http%3A%2F%2Flocalhost%3A3000%2F",
    )
    await waitFor(() => {
        expect(toast.showMessage).toHaveBeenCalledTimes(1)
    })
})

test("DownloadAsPDFButton ignores unregistered query parameters", async () => {
    history.push("?unregister_key=value&nr_dates=4")
    render(<DownloadAsPDFButton report_uuid="report_uuid" />)
    await clickDownload()
    expect(get_report_pdf.get_report_pdf).toHaveBeenCalledWith(
        "report_uuid",
        "?nr_dates=4&report_url=http%3A%2F%2Flocalhost%3A3000%2F%3Fnr_dates%3D4",
    )
})

test("DownloadAsPDFButton stops loading after returning pdf", async () => {
    HTMLAnchorElement.prototype.click = vi.fn() // Prevent "Not implemented: navigation (except hash changes)"
    window.URL.createObjectURL = vi.fn()
    render(<DownloadAsPDFButton />)
    await clickDownload()
    expectButtonIsNotLoading()
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
})

test("DownloadAsPDFButton stops loading after receiving error", async () => {
    get_report_pdf.get_report_pdf.mockImplementation(() =>
        Promise.resolve({ ok: false, status: "403", statusText: "access denied" }),
    )
    render(<DownloadAsPDFButton />)
    await clickDownload()
    expectButtonIsNotLoading()
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "PDF rendering failed", "HTTP code 403: access denied")
})

test("DownloadAsPDFButton catches errors", async () => {
    get_report_pdf.get_report_pdf.mockImplementation(() => Promise.reject(new Error("Oops")))
    render(<DownloadAsPDFButton />)
    await clickDownload()
    expectButtonIsNotLoading()
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not fetch PDF report", "Error: Oops")
})
