import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { DataModelContext } from "../../context/DataModel"
import * as reportCsv from "../../report/report_csv"
import * as download from "../download"
import { SnackbarAlerts } from "../SnackbarAlerts"
import { ExportReportCsvButton } from "./ExportReportCsvButton"

beforeEach(() => {
    globalThis.URL.createObjectURL = vi.fn(() => "#dummy")
})

afterEach(() => vi.restoreAllMocks())

function renderButton({ showMessage = vi.fn() } = {}) {
    render(
        <DataModelContext value={{}}>
            <SnackbarAlerts messages={[]} showMessage={showMessage}>
                <ExportReportCsvButton report={{ report_uuid: "report_uuid" }} measurements={[]} dates={[new Date()]} />
            </SnackbarAlerts>
        </DataModelContext>,
    )
}

it("downloads a CSV file", async () => {
    const triggerDownload = vi.spyOn(download, "triggerDownload").mockImplementation(() => {})
    vi.spyOn(reportCsv, "reportToCSV").mockReturnValue("Subject,Metric\r\nSubject 1,M1")
    renderButton()
    await userEvent.click(screen.getByText(/Export as CSV/))
    expect(triggerDownload).toHaveBeenCalledTimes(1)
    const [blob, filename] = triggerDownload.mock.calls[0]
    expect(blob.type).toContain("text/csv")
    expect(filename).toMatch(/^Quality-time-report-report_uuid-.*\.csv$/)
    // The CSV is generated with the list separator of the user's locale (a comma in the test environment's en-US locale)
    expect(reportCsv.reportToCSV).toHaveBeenCalledWith(expect.anything(), [], [expect.any(Date)], undefined, {}, ",")
    // The file content equals the generated CSV (the leading UTF-8 BOM is stripped by Blob.text() when decoding)
    expect(await blob.text()).toBe("Subject,Metric\r\nSubject 1,M1")
})

it("shows a message when CSV generation fails", async () => {
    const showMessage = vi.fn()
    vi.spyOn(reportCsv, "reportToCSV").mockImplementation(() => {
        throw new Error("Boom")
    })
    renderButton({ showMessage: showMessage })
    await userEvent.click(screen.getByText(/Export as CSV/))
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Could not export report to CSV",
        description: "Error: Boom",
    })
})
