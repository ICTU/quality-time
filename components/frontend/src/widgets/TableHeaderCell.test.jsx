import { Table, TableHead, TableRow } from "@mui/material"
import { render } from "@testing-library/react"

import { useSettings } from "../app_ui_settings"
import { expectText, expectTextAfterWait, hoverText } from "../testUtils"
import { SortableTableHeaderCell, UnsortableTableHeaderCell } from "./TableHeaderCell"

function SortableTableHeaderCellWrapper({ help }) {
    const settings = useSettings()
    return (
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
        </Table>
    )
}

function renderSortableTableHeaderCell(help) {
    render(<SortableTableHeaderCellWrapper help={help} />)
}

it("shows the label of the sortable header", () => {
    renderSortableTableHeaderCell()
    expectText(/Header/)
})

it("shows the help of the sortable header", async () => {
    renderSortableTableHeaderCell("Help")
    await hoverText(/Header/)
    await expectTextAfterWait(/Help/)
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
    expectText(/Header/)
})

it("shows the help of the unsortable header", async () => {
    renderUnsortableTableHeaderCell("Help")
    await hoverText(/Header/)
    await expectTextAfterWait(/Help/)
})

it("shows the icon of the unsortable header", () => {
    const icon = <span>Icon</span>
    renderUnsortableTableHeaderCell(null, icon)
    expectText(/Icon/)
})
