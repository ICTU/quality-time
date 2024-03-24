import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { DownloadAsPDFButton } from "./DownloadAsPDFButton"
import * as fetch_server_api from "../api/fetch_server_api"

test("DownloadAsPDFButton has the correct label for reports overview", () => {
    render(<DownloadAsPDFButton />)
    expect(screen.getAllByLabelText(/reports overview as PDF/).length).toBe(1)
})

test("DownloadAsPDFButton has the correct label for a report", () => {
    render(<DownloadAsPDFButton report_uuid={"report_uuid"} />)
    expect(screen.getAllByLabelText(/report as PDF/).length).toBe(1)
})

const test_report = { report_uuid: "report_uuid" }

test("DownloadAsPDFButton indicates loading on click", async () => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) })
    render(<DownloadAsPDFButton report={test_report} report_uuid="report_uuid" />)
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Download/))
    })
    expect(screen.getByLabelText(/Download/).className).toContain("loading")
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith(
        "get",
        "report/report_uuid/pdf?report_url=http%3A%2F%2Flocalhost%2F",
        {},
        "application/pdf",
    )
})

test("DownloadAsPDFButton ignores unregistered query parameters", async () => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) })
    history.push("?unregister_key=value&nr_dates=4")
    render(<DownloadAsPDFButton report={test_report} report_uuid="report_uuid" />)
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Download/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith(
        "get",
        "report/report_uuid/pdf?nr_dates=4&report_url=http%3A%2F%2Flocalhost%2F%3Fnr_dates%3D4",
        {},
        "application/pdf",
    )
})

test("DownloadAsPDFButton ignores a second click", async () => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) })
    render(<DownloadAsPDFButton report={test_report} />)
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Download/))
    })
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Download/))
    })
    expect(screen.getByLabelText(/Download/).className).toContain("loading")
})

test("DownloadAsPDFButton stops loading after returning pdf", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue("pdf")
    HTMLAnchorElement.prototype.click = jest.fn() // Prevent "Not implemented: navigation (except hash changes)"
    window.URL.createObjectURL = jest.fn()
    render(<DownloadAsPDFButton report={test_report} />)
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Download/))
    })
    expect(screen.getByLabelText(/Download/).className).not.toContain("loading")
})

test("DownloadAsPDFButton stops loading after receiving error", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false })
    render(<DownloadAsPDFButton report={test_report} />)
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Download/))
    })
    expect(screen.getByLabelText(/Download/).className).not.toContain("loading")
})
