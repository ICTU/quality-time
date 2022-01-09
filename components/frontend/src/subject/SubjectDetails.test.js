import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { datamodel, report } from "../__fixtures__/fixtures";
import { DataModel } from '../context/DataModel';
import { SubjectDetails } from './SubjectDetails';

function renderSubjectDetails(handleSort, sortColumn, setSortColumn, sortDirection, setSortDirection) {
    return render(
        <DataModel.Provider value={datamodel}>
            <SubjectDetails
                subject_uuid="subject_uuid"
                metrics={report.subjects.subject_uuid.metrics}
                report={report}
                hiddenColumns={[]}
                visibleDetailsTabs={[]}
                handleSort={(column) => handleSort(column)}
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

it('changes the sort order when a column header is clicked', () => {
    const handleSort = jest.fn()
    const setSortColumn = jest.fn()
    const setSortDirection = jest.fn()
    renderSubjectDetails(handleSort, "tags", setSortColumn, "ascending", setSortDirection)
    fireEvent.click(screen.queryByText(/Metric/))
    expect(handleSort).toHaveBeenCalledWith("name")
});