import { act, render, screen } from "@testing-library/react";
import { Subject } from "./Subject";
import { DataModel } from "../context/DataModel";
import { datamodel, report } from "../__fixtures__/fixtures";

function renderSubject(dates, hiddenTags, hideMetricsNotRequiringAction, sortColumn, sortDirection, reportDate) {
    render(
        <DataModel.Provider value={datamodel}>
            <Subject
                dates={dates}
                handleSort={() => { /* Dummy implementation */ }}
                hiddenTags={hiddenTags ?? []}
                measurements={[]}
                report={report}
                report_date={reportDate}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                subject_uuid="subject_uuid"
                tags={[]}
                hiddenColumns={[]}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                visibleDetailsTabs={[]} />
        </DataModel.Provider>
    )
}

it('shows the subject title', async () => {
    await act(async () => { renderSubject([new Date(2022, 3, 26)]) });
    expect(screen.queryAllByText("Subject 1 title").length).toBe(1);
})

it('hides metrics not requiring action', async () => {
    await act(async () => { renderSubject([new Date(2022, 3, 26)], [], true) });
    expect(screen.queryAllByText(/M\d/).length).toBe(1);
})

it('hides the subject if all metrics are hidden', async () => {
    await act(async () => { renderSubject([], ["tag", "other tag"]) });
    expect(screen.queryAllByText("Subject 1 title").length).toBe(0);
})

function expectOrder(metricNames) {
    expect(screen.getAllByText(/M\d/).map((element) => element.innerHTML)).toStrictEqual(metricNames)
}

for (const attribute of ["name", "measurement", "target", "comment", "source", "issues", "tags", "unit", "status", "time_left", "overrun"]) {
    for (const order of ["ascending", "descending"]) {
        it('sorts metrics by attribute', async () => {
            await act(async () => { renderSubject([], [], false, attribute, order) });
            expectOrder(order === "ascending" ? ["M1", "M2"] : ["M2", "M1"])
        })
    }
}
