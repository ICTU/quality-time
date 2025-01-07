import { Table } from "@mui/material"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { SubjectTableHeader } from "./SubjectTableHeader"

function renderSubjectTableHeader(columnDates) {
    const settings = createTestableSettings()
    render(
        <Table>
            <SubjectTableHeader columnDates={columnDates} settings={settings} />
        </Table>,
    )
}

beforeEach(() => {
    history.push("")
})

it("shows the column dates and unit", () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    renderSubjectTableHeader([date1, date2])
    ;[
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
    ].forEach((header) => expect(screen.getAllByText(header).length).toBe(1))
    ;["Trend (7 days)", "Status", "Measurement", "Target"].forEach((header) =>
        expect(screen.queryAllByText(header).length).toBe(0),
    )
})

it("does not show the column dates", () => {
    const date1 = new Date("2022-02-02")
    renderSubjectTableHeader([date1])
    ;[date1.toLocaleDateString(), "Overrun"].forEach((header) => expect(screen.queryAllByText(header).length).toBe(0))
    ;[
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
    ].forEach((header) => expect(screen.queryAllByText(header).length).toBe(1))
})

it("hides columns", () => {
    history.push("?hidden_columns=trend,status,measurement,target,source,comment,issues,tags")
    const date1 = new Date("2022-02-02")
    renderSubjectTableHeader([date1])
    ;["Trend (7 days)", "Status", "Measurement", "Target", "Sources", "Comment", "Issues", "Tags"].forEach((header) =>
        expect(screen.queryAllByText(header).length).toBe(0),
    )
})

it("hides the delta columns", () => {
    history.push("?hidden_columns=delta")
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    renderSubjectTableHeader([date1, date2])
    expect(screen.queryAllByText("𝚫").length).toBe(0)
})

it("shows help for column headers", async () => {
    const date1 = new Date("2022-02-02")
    renderSubjectTableHeader([date1])
    await userEvent.hover(screen.getByText("Metric"))
    await waitFor(() => {
        expect(screen.queryByText(/Click the column header to sort the metrics by name/)).not.toBe(null)
    })
})

it("shows help for delta column headers", async () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    renderSubjectTableHeader([date1, date2])
    await userEvent.hover(screen.getByText(/𝚫/))
    await waitFor(() => {
        expect(screen.queryByText(/shows the difference/)).not.toBe(null)
    })
})
