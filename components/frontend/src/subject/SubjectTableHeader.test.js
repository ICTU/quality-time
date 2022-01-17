import React from 'react';
import { Table } from 'semantic-ui-react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { SubjectTableHeader } from './SubjectTableHeader';

function renderSubjectTableHeader(mockCallback, visibleDetailsTabs) {
    return render(
        <Table>
            <SubjectTableHeader
                clearVisibleDetailsTabs={mockCallback}
                columnDates={[]}
                hiddenColumns={[]}
                setDateInterval={mockCallback}
                visibleDetailsTabs={visibleDetailsTabs ?? []}
            />
        </Table>
    )
}

it('sets the nr of days', async () => {
    const mockCallback = jest.fn()
    renderSubjectTableHeader(mockCallback)
    await act(async () => fireEvent.click(screen.getAllByTestId("HamburgerMenu")[0]))
    fireEvent.click(screen.getByText(/1 day/));
    expect(mockCallback).toHaveBeenCalledWith(1);
});

it('sets the nr of weeks', async () => {
    const mockCallback = jest.fn()
    renderSubjectTableHeader(mockCallback)
    await act(async () => fireEvent.click(screen.getAllByTestId("HamburgerMenu")[0]))
    fireEvent.click(screen.getByText(/2 weeks/));
    expect(mockCallback).toHaveBeenCalledWith(14);
});

it('collapses all metrics', async () => {
    const mockCallback = jest.fn()
    renderSubjectTableHeader(mockCallback, ["tab1", "tab2"])
    await act(async () => fireEvent.click(screen.getAllByTestId("HamburgerMenu")[0]))
    fireEvent.click(screen.getByText(/Collapse all metrics/));
    expect(mockCallback).toHaveBeenCalled();
})
