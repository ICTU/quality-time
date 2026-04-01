import { Table, TableBody } from "@mui/material"
import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { render, renderHook, screen } from "@testing-library/react"

import { useLanguageURLSearchQuery } from "../app_ui_settings"
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

it("has no accessibility violations", async () => {
    const { container } = renderSourceEntity({})
    await expectNoAccessibilityViolations(container)
})

it("renders the unconfirmed status", async () => {
    renderSourceEntity({})
    clickButton()
    expectText(/Unconfirmed/, 2)
    expect(screen.getAllByText(/Unconfirmed/)[0].closest("tr").className).toContain("warning_status")
})

it("renders the fixed status", async () => {
    renderSourceEntity({ status: "fixed" })
    expectText(/Fixed/)
})

it("renders the status end date", async () => {
    renderSourceEntity({ status: "fixed", statusEndDate: "3000-01-01" })
    const language = renderHook(() => useLanguageURLSearchQuery().value)
    const expectedDate = renderHook(() => formatDate(new Date("3000-01-01"), language.result.current))
    expectText(RegExp(expectedDate.result.current))
})

it("does not render the status end date if the status is unconfirmed", async () => {
    renderSourceEntity({ status: "unconfirmed", statusEndDate: "3000-01-01" })
    const language = renderHook(() => useLanguageURLSearchQuery().value)
    const expectedDate = renderHook(() => formatDate(new Date("3000-01-01"), language.result.current))
    expectNoText(RegExp(expectedDate.result.current))
})

it("renders the status rationale", async () => {
    renderSourceEntity({ status: "fixed", rationale: "Why?" })
    expectText(/Why\?/)
})

it("renders the first seen datetime", async () => {
    renderSourceEntity({ firstSeen: "2023-07-17" })
    expectText(/ago/)
})

it("renders the status and rationale past end date", async () => {
    renderSourceEntity({
        status: "fixed",
        statusEndDate: "2000-01-01",
        hideIgnoredEntities: true,
        rationale: "Because",
    })
    const language = renderHook(() => useLanguageURLSearchQuery().value)
    const expectedDate = renderHook(() => formatDate(new Date("2000-01-01"), language.result.current))
    expectText(RegExp(expectedDate.result.current))
    expectText(/Because/)
})

it("renders nothing if the status is to be ignored", async () => {
    renderSourceEntity({ status: "fixed", hideIgnoredEntities: true })
    expectNoText(/Fixed/)
})
