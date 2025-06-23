import { Table, TableHead, TableRow } from "@mui/material"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { SortableTableHeaderCell, UnsortableTableHeaderCell } from "./TableHeaderCell"

function renderSortableTableHeaderCell(help) {
    const settings = createTestableSettings()
    render(
        <Table>
            <TableHead>
                <TableRow>
                    <SortableTableHeaderCell
                        label="Header"
                        help={help}
                        sortColumn={settings.sortColumn.value}
                        sortDirection={settings.sortDirection.value}
                    />
                </TableRow>
            </TableHead>
        </Table>,
    )
}

it("shows the label of the sortable header", () => {
    renderSortableTableHeaderCell()
    expect(screen.queryAllByText(/Header/).length).toBe(1)
})

it("shows the help of the sortable header", async () => {
    renderSortableTableHeaderCell("Help")
    await userEvent.hover(screen.queryByText(/Header/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Help/).length).toBe(1)
    })
})

function renderUnsortableTableHeaderCell(help, icon) {
    render(
        <Table>
            <TableHead>
                <TableRow>
                    <UnsortableTableHeaderCell label="Header" help={help} icon={icon} />
                </TableRow>
            </TableHead>
        </Table>,
    )
}

it("shows the label of the unsortable header", () => {
    renderUnsortableTableHeaderCell()
    expect(screen.queryAllByText(/Header/).length).toBe(1)
})

it("shows the help of the unsortable header", async () => {
    renderUnsortableTableHeaderCell("Help")
    await userEvent.hover(screen.queryByText(/Header/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Help/).length).toBe(1)
    })
})

it("shows the icon of the unsortable header", () => {
    const icon = <span>Icon</span>
    renderUnsortableTableHeaderCell(null, icon)
    expect(screen.queryAllByText(/Icon/).length).toBe(1)
})
