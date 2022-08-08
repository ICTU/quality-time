import React from 'react';
import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '@testing-library/react';
import { Table } from 'semantic-ui-react'
import { SortableTableHeaderCell } from './SortableTableHeaderCell';

function renderSortableTableHeaderCell(help) {
    render(
        <Table>
            <Table.Header>
                <Table.Row>
                    <SortableTableHeaderCell label="Header" help={help}/>
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
    expect(screen.queryAllByText(/Header/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Header/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Help/).length).toBe(0)
    })
});
