import { Table } from "@mui/material"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SubjectTableHeader } from "./SubjectTableHeader"

function renderSubjectTableHeader(columnDates, columnsToHide) {
    const settings = createTestableSettings()
    return render(
        <Table>
            <SubjectTableHeader columnDates={columnDates} columnsToHide={columnsToHide ?? []} settings={settings} />
        </Table>,
    )
}

beforeEach(() => {
    history.push("")
})

it("shows the column dates and unit", async () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    const { container } = renderSubjectTableHeader([date1, date2])
    const headers = [
        date1.toLocaleDateString(),
        "𝚫",
        date2.toLocaleDateString(),
        "Unit",
        "Sources",
        "Time left",
        "Overrun",
        "Comment",
        "Issues",
        "Tags",
    ]
    headers.forEach((header) => expect(screen.getAllByText(header).length).toBe(1))
    await expectNoAccessibilityViolations(container)
})

it("does not show the column dates", async () => {
    const date1 = new Date("2022-02-02")
    const { container } = renderSubjectTableHeader([date1])
    const headers = [
        "Trend (7 days)",
        "Status",
        "Measurement",
        "Target",
        "Unit",
        "Sources",
        "Time left",
        "Comment",
        "Issues",
        "Tags",
    ]
    headers.forEach((header) => expect(screen.queryAllByText(header).length).toBe(1))
    await expectNoAccessibilityViolations(container)
})

it("hides columns", async () => {
    const date1 = new Date("2022-02-02")
    const columns = ["trend", "status", "measurement", "target", "source", "comment", "issues", "tags"]
    const { container } = renderSubjectTableHeader([date1], columns)
    const headers = ["Trend (7 days)", "Status", "Measurement", "Target", "Sources", "Comment", "Issues", "Tags"]
    headers.forEach((header) => expect(screen.queryAllByText(header).length).toBe(0))
    await expectNoAccessibilityViolations(container)
})

it("hides the delta columns", async () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    const { container } = renderSubjectTableHeader([date1, date2], ["delta"])
    expect(screen.queryAllByText("𝚫").length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("shows help for column headers", async () => {
    const date1 = new Date("2022-02-02")
    const { container } = renderSubjectTableHeader([date1])
    await userEvent.hover(screen.getByText("Metric"))
    await waitFor(() => {
        expect(screen.queryByText(/Click the column header to sort the metrics by name/)).not.toBe(null)
    })
    await expectNoAccessibilityViolations(container)
})

it("shows help for delta column headers", async () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    const { container } = renderSubjectTableHeader([date1, date2])
    await userEvent.hover(screen.getByText(/𝚫/))
    await waitFor(() => {
        expect(screen.queryByText(/shows the difference/)).not.toBe(null)
    })
    await expectNoAccessibilityViolations(container)
})
