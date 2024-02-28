import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '@testing-library/react';
import { Table } from 'semantic-ui-react'
import { createTestableSettings } from '../__fixtures__/fixtures';
import { SortableTableHeaderCell, UnsortableTableHeaderCell } from './TableHeaderCell';

function renderSortableTableHeaderCell(help) {
    const settings = createTestableSettings()
    render(
        <Table>
            <Table.Header>
                <Table.Row>
                    <SortableTableHeaderCell label="Header" help={help} sortColumn={settings.sortColumn} sortDirection={settings.sortDirection}/>
                </Table.Row>
            </Table.Header>
        </Table>
    )
}

it('shows the label', () => {
    renderSortableTableHeaderCell()
    expect(screen.queryAllByText(/Header/).length).toBe(1)
});

it('shows the help', async () => {
    renderSortableTableHeaderCell("Help")
    await userEvent.hover(screen.queryByText(/Header/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Help/).length).toBe(1)
    })
});

function renderUnsortableTableHeaderCell(help) {
    render(
        <Table>
            <Table.Header>
                <Table.Row>
                    <UnsortableTableHeaderCell label="Header" help={help}/>
                </Table.Row>
            </Table.Header>
        </Table>
    )
}

it('shows the label', () => {
    renderUnsortableTableHeaderCell()
    expect(screen.queryAllByText(/Header/).length).toBe(1)
});

it('shows the help', async () => {
    renderUnsortableTableHeaderCell("Help")
    await userEvent.hover(screen.queryByText(/Header/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Help/).length).toBe(1)
    })
});
