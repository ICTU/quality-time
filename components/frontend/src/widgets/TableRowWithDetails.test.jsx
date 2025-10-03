import { Table, TableBody, TableCell } from "@mui/material"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { clickButton, expectNoText, expectText } from "../testUtils"
import { TableRowWithDetails } from "./TableRowWithDetails"

function renderTableRowWithDetails(expanded, onExpand) {
    render(
        <Table>
            <TableBody>
                <TableRowWithDetails expanded={expanded} onExpand={onExpand} details={"Details"}>
                    <TableCell></TableCell>
                </TableRowWithDetails>
            </TableBody>
        </Table>,
    )
}

it("shows the details when expanded", () => {
    renderTableRowWithDetails(true)
    expectText(/Details/)
})

it("does not show the details when collapsed", () => {
    renderTableRowWithDetails(false)
    expectNoText(/Details/)
})

it("calls the expand callback when clicked", () => {
    const onExpand = vi.fn()
    renderTableRowWithDetails(false, onExpand)
    clickButton()
    expect(onExpand).toHaveBeenCalledWith(true)
})

it("calls the expand callback on keypress", async () => {
    const onExpand = vi.fn()
    renderTableRowWithDetails(false, onExpand)
    await userEvent.type(screen.getByRole("button"), "x")
    expect(onExpand).toHaveBeenCalledWith(true)
})
