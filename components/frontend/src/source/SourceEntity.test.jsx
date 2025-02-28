import { Table, TableBody } from "@mui/material"
import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { fireEvent, render, renderHook, screen } from "@testing-library/react"

import { formatDate } from "../locale"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SourceEntity } from "./SourceEntity"

function renderSourceEntity({
    status = "unconfirmed",
    status_end_date = "",
    rationale = "",
    hide_ignored_entities = false,
    first_seen = null,
}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Table>
                <TableBody>
                    <SourceEntity
                        entity={{ attr1: "good", attr2: "bad", first_seen: first_seen }}
                        entity_attributes={[{ key: "attr1" }, { key: "attr2", color: { bad: "warning" } }]}
                        entity_name="entity"
                        hide_ignored_entities={hide_ignored_entities}
                        rationale={rationale}
                        status={status}
                        status_end_date={status_end_date}
                    />
                </TableBody>
            </Table>
        </LocalizationProvider>,
    )
}

it("renders the unconfirmed status", async () => {
    const { container } = renderSourceEntity({})
    fireEvent.click(screen.getByRole("button"))
    expect(screen.getAllByText(/Unconfirmed/).length).toBe(2)
    expect(screen.getAllByText(/Unconfirmed/)[0].closest("tr").className).toContain("warning_status")
    await expectNoAccessibilityViolations(container)
})

it("renders the fixed status", async () => {
    const { container } = renderSourceEntity({ status: "fixed" })
    expect(screen.getAllByText(/Fixed/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the status end date", async () => {
    const { container } = renderSourceEntity({ status: "fixed", status_end_date: "3000-01-01" })
    const expectedDate = renderHook(() => formatDate(new Date("3000-01-01")))
    expect(screen.getAllByText(RegExp(expectedDate.result.current)).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not render the status end date if the status is unconfirmed", async () => {
    const { container } = renderSourceEntity({ status: "unconfirmed", status_end_date: "3000-01-01" })
    const expectedDate = renderHook(() => formatDate(new Date("3000-01-01")))
    expect(screen.queryAllByText(RegExp(expectedDate.result.current)).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders the status rationale", async () => {
    const { container } = renderSourceEntity({ status: "fixed", rationale: "Why?" })
    expect(screen.getAllByText(/Why\?/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the first seen datetime", async () => {
    const { container } = renderSourceEntity({ first_seen: "2023-07-17" })
    expect(screen.getAllByText(/ago/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the status and rationale past end date", async () => {
    const { container } = renderSourceEntity({
        status: "fixed",
        status_end_date: "2000-01-01",
        hide_ignored_entities: true,
        rationale: "Because",
    })
    const expectedDate = renderHook(() => formatDate(new Date("2000-01-01")))
    expect(screen.getAllByText(RegExp(expectedDate.result.current)).length).toBe(1)
    expect(screen.getAllByText(/Because/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders nothing if the status is to be ignored", async () => {
    const { container } = renderSourceEntity({ status: "fixed", hide_ignored_entities: true })
    expect(screen.queryAllByText(/Fixed/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})
