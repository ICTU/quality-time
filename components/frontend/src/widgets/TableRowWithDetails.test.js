import React from 'react';
import { Table } from 'semantic-ui-react'
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event'
import { TableRowWithDetails } from './TableRowWithDetails';

function renderTableRowWithDetails(expanded, onExpand) {
    render(
        <Table>
            <Table.Body>
                <TableRowWithDetails expanded={expanded} onExpand={onExpand} details={"Details"}/>
            </Table.Body>
        </Table>
    )
}

it('shows the details when expanded', () => {
    renderTableRowWithDetails(true)
    expect(screen.queryAllByText(/Details/).length).toBe(1)
});

it('does not show the details when collapsed', () => {
    renderTableRowWithDetails(false)
    expect(screen.queryAllByText(/Details/).length).toBe(0)
});

it('calls the expand callback when clicked', () => {
    const onExpand = jest.fn()
    renderTableRowWithDetails(false, onExpand)
    fireEvent.click(screen.getByRole("button"))
    expect(onExpand).toHaveBeenCalledWith(true)
});

it('calls the expand callback on keypress', () => {
    const onExpand = jest.fn()
    renderTableRowWithDetails(false, onExpand)
    userEvent.type(screen.getByRole("button"), "x")
    expect(onExpand).toHaveBeenCalledWith(true)
});
