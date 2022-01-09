import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { datamodel, report } from "../__fixtures__/fixtures";
import { DataModel } from '../context/DataModel';
import { SubjectDetails } from './SubjectDetails';

function renderSubjectDetails(setSortDirection) {
    return render(
        <DataModel.Provider value={datamodel}>
            <SubjectDetails
                subject_uuid="subject_uuid"
                metrics={report.subjects.subject_uuid.metrics}
                report={report}
                hiddenColumns={[]}
                visibleDetailsTabs={[]}
                sortDirection="ascending"
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
    const setSortDirection = jest.fn()
    renderSubjectDetails(setSortDirection)
    fireEvent.click(screen.queryByText(/Metric/))
    fireEvent.click(screen.queryByText(/Metric/))
    expect(setSortDirection).toHaveBeenCalledWith("descending")
});
