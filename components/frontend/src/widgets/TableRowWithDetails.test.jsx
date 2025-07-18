import { Table, TableBody, TableCell } from "@mui/material"
import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

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
    expect(screen.queryAllByText(/Details/).length).toBe(1)
})

it("does not show the details when collapsed", () => {
    renderTableRowWithDetails(false)
    expect(screen.queryAllByText(/Details/).length).toBe(0)
})

it("calls the expand callback when clicked", () => {
    const onExpand = vi.fn()
    renderTableRowWithDetails(false, onExpand)
    fireEvent.click(screen.getByRole("button"))
    expect(onExpand).toHaveBeenCalledWith(true)
})

it("calls the expand callback on keypress", async () => {
    const onExpand = vi.fn()
    renderTableRowWithDetails(false, onExpand)
    await userEvent.type(screen.getByRole("button"), "x")
    expect(onExpand).toHaveBeenCalledWith(true)
})
