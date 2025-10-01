import { Table, TableBody } from "@mui/material"
import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { render, renderHook, screen } from "@testing-library/react"

import { formatDate } from "../datetime"
import { clickButton, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { SourceEntity } from "./SourceEntity"

function renderSourceEntity({
    status = "unconfirmed",
    statusEndDate = "",
    rationale = "",
    hideIgnoredEntities = false,
    firstSeen = null,
}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Table>
                <TableBody>
                    <SourceEntity
                        columnsToHide={[]}
                        entity={{ attr1: "good", attr2: "bad", first_seen: firstSeen }}
                        entityAttributes={[{ key: "attr1" }, { key: "attr2", color: { bad: "warning" } }]}
                        entityName="entity"
                        hideIgnoredEntities={hideIgnoredEntities}
                        rationale={rationale}
                        status={status}
                        statusEndDate={statusEndDate}
                    />
                </TableBody>
            </Table>
        </LocalizationProvider>,
    )
}

it("renders the unconfirmed status", async () => {
    const { container } = renderSourceEntity({})
    clickButton()
    expectText(/Unconfirmed/, 2)
    expect(screen.getAllByText(/Unconfirmed/)[0].closest("tr").className).toContain("warning_status")
    await expectNoAccessibilityViolations(container)
})

it("renders the fixed status", async () => {
    const { container } = renderSourceEntity({ status: "fixed" })
    expectText(/Fixed/)
    await expectNoAccessibilityViolations(container)
})

it("renders the status end date", async () => {
    const { container } = renderSourceEntity({ status: "fixed", statusEndDate: "3000-01-01" })
    const expectedDate = renderHook(() => formatDate(new Date("3000-01-01")))
    expectText(RegExp(expectedDate.result.current))
    await expectNoAccessibilityViolations(container)
})

it("does not render the status end date if the status is unconfirmed", async () => {
    const { container } = renderSourceEntity({ status: "unconfirmed", statusEndDate: "3000-01-01" })
    const expectedDate = renderHook(() => formatDate(new Date("3000-01-01")))
    expectNoText(RegExp(expectedDate.result.current))
    await expectNoAccessibilityViolations(container)
})

it("renders the status rationale", async () => {
    const { container } = renderSourceEntity({ status: "fixed", rationale: "Why?" })
    expectText(/Why\?/)
    await expectNoAccessibilityViolations(container)
})

it("renders the first seen datetime", async () => {
    const { container } = renderSourceEntity({ firstSeen: "2023-07-17" })
    expectText(/ago/)
    await expectNoAccessibilityViolations(container)
})

it("renders the status and rationale past end date", async () => {
    const { container } = renderSourceEntity({
        status: "fixed",
        statusEndDate: "2000-01-01",
        hideIgnoredEntities: true,
        rationale: "Because",
    })
    const expectedDate = renderHook(() => formatDate(new Date("2000-01-01")))
    expectText(RegExp(expectedDate.result.current))
    expectText(/Because/)
    await expectNoAccessibilityViolations(container)
})

it("renders nothing if the status is to be ignored", async () => {
    const { container } = renderSourceEntity({ status: "fixed", hideIgnoredEntities: true })
    expectNoText(/Fixed/)
    await expectNoAccessibilityViolations(container)
})
