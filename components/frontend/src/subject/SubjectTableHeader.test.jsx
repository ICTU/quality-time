import { Table } from "@mui/material"
import { render } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { expectNoAccessibilityViolations, expectNoText, expectText, expectTextAfterWait, hoverText } from "../testUtils"
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
    headers.forEach((header) => expectText(header))
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
    headers.forEach((header) => expectText(header))
    await expectNoAccessibilityViolations(container)
})

it("hides columns", async () => {
    const date1 = new Date("2022-02-02")
    const columns = ["trend", "status", "measurement", "target", "source", "comment", "issues", "tags"]
    const { container } = renderSubjectTableHeader([date1], columns)
    const headers = ["Trend (7 days)", "Status", "Measurement", "Target", "Sources", "Comment", "Issues", "Tags"]
    headers.forEach((header) => expectNoText(header))
    await expectNoAccessibilityViolations(container)
})

it("hides the delta columns", async () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    const { container } = renderSubjectTableHeader([date1, date2], ["delta"])
    expectNoText("𝚫")
    await expectNoAccessibilityViolations(container)
})

it("shows help for column headers", async () => {
    const date1 = new Date("2022-02-02")
    const { container } = renderSubjectTableHeader([date1])
    await hoverText("Metric")
    await expectTextAfterWait(/Click the column header to sort the metrics by name/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for delta column headers", async () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    const { container } = renderSubjectTableHeader([date1, date2])
    await hoverText(/𝚫/)
    await expectTextAfterWait(/shows the difference/)
    await expectNoAccessibilityViolations(container)
})
