import React from 'react';
import { render, screen } from "@testing-library/react";
import { DataModel } from '../context/DataModel';
import { Subjects } from './Subjects';
import { datamodel, report } from "../__fixtures__/fixtures";

function renderSubjects() {
    return render(
        <DataModel.Provider value={datamodel}>
            <Subjects
                dates={[]}
                hiddenColumns={[]}
                history={history}
                measurements={[]}
                reports={[report]}
                reportsToShow={[report]}
                tags={[]}
                visibleDetailsTabs={[]}
            />
        </DataModel.Provider>
    )
}

it("shows the subjects", () => {
    renderSubjects();
    expect(screen.getAllByText(/Subject/).length).toBe(2);
})
