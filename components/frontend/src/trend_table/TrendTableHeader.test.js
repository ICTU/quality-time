import React from 'react';
import { Table } from 'semantic-ui-react';
import { fireEvent, render, screen } from '@testing-library/react';
import { TrendTableHeader } from './TrendTableHeader';

function renderTrendTableHeader(setTrendTableInterval) {
    return render(
        <Table>
            <TrendTableHeader hiddenColumns={[]} columnDates={[]} setTrendTableInterval={setTrendTableInterval} />
        </Table>
    )
}

it('sets the nr of days', () => {
    const mockCallback = jest.fn()
    renderTrendTableHeader(mockCallback)
    fireEvent.click(screen.getByText(/1 day/));
    expect(mockCallback).toHaveBeenCalledWith(1);
});

it('sets the nr of weeks', () => {
    const mockCallback = jest.fn()
    renderTrendTableHeader(mockCallback)
    fireEvent.click(screen.getByText(/2 weeks/));
    expect(mockCallback).toHaveBeenCalledWith(14);
});
