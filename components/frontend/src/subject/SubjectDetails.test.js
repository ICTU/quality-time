import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { datamodel, report } from "../__fixtures__/fixtures";
import { DataModel } from '../context/DataModel';
import { SubjectDetails } from './SubjectDetails';

function renderSubjectDetails(sortColumn, setSortColumn, sortDirection, setSortDirection) {
    return render(
        <DataModel.Provider value={datamodel}>
            <SubjectDetails
                subject_uuid="subject_uuid"
                metrics={report.subjects.subject_uuid.metrics}
                report={report}
                hiddenColumns={[]}
                visibleDetailsTabs={[]}
                sortColumn={sortColumn}
                setSortColumn={(column) => setSortColumn(column)}
                sortDirection={sortDirection}
                setSortDirection={(direction) => setSortDirection(direction)}
                />
        </DataModel.Provider>
    )
}

it('displays one row per metric', () => {
    renderSubjectDetails()
    expect(screen.queryAllByText("M1").length).toBe(1)
    expect(screen.queryAllByText("M2").length).toBe(1)
})

it('changes the sort direction when a column header is clicked', () => {
    const setSortColumn = jest.fn()
    const setSortDirection = jest.fn()
    renderSubjectDetails("name", setSortColumn, "ascending", setSortDirection)
    fireEvent.click(screen.queryByText(/Metric/))
    expect(setSortDirection).toHaveBeenCalledWith("descending")
});

it('changes the sort column when a column header is clicked', () => {
    const setSortColumn = jest.fn()
    const setSortDirection = jest.fn()
    renderSubjectDetails("tags", setSortColumn, "ascending", setSortDirection)
    fireEvent.click(screen.queryByText(/Metric/))
    expect(setSortColumn).toHaveBeenCalledWith("name")
});