import { act, render, screen } from "@testing-library/react";
import { Subject } from "./Subject";
import * as fetch_server_api from '../api/fetch_server_api';
import { DataModel } from "../context/DataModel";
import { datamodel, report } from "../__fixtures__/fixtures";

function renderSubject(dates, hideMetricsNotRequiringAction, sortColumn, sortDirection) {
    render(
        <DataModel.Provider value={datamodel}>
            <Subject
                dates={dates}
                handleSort={() => { /* Dummy implementation */ }}
                report={report}
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

it('fetches measurements if nr dates > 1', async () => {
    jest.mock("../api/fetch_server_api.js")
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, measurements: [] });
    await act(async () => { renderSubject([new Date(2022, 3, 25), new Date(2022, 3, 26)]) });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "subject/subject_uuid/measurements", undefined);
})

it('does not fetch measurements if nr dates == 1', async () => {
    jest.mock("../api/fetch_server_api.js")
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, measurements: [] });
    await act(async () => { renderSubject([new Date(2022, 3, 26)]) });
    expect(fetch_server_api.fetch_server_api).not.toHaveBeenCalled();
})

it('shows the subject title', async () => {
    await act(async () => { renderSubject([new Date(2022, 3, 26)]) });
    expect(screen.queryAllByText("Subject 1 title").length).toBe(1);
})

it('hides metrics not requiring action', async () => {
    await act(async () => { renderSubject([new Date(2022, 3, 26)], true) });
    expect(screen.queryAllByText(/M\d/).length).toBe(1);
})

function expectOrder(metricNames) {
    expect(screen.getAllByText(/M\d/).map((element) => element.innerHTML)).toStrictEqual(metricNames)
}

for (const attribute of ["name", "measurement", "target", "comment", "source", "issues", "tags", "unit", "status", "time_left"]) {
    for (const order of ["ascending", "descending"]) {
        it('sorts metrics by attribute', async () => {
            await act(async () => { renderSubject([], false, attribute, order) });
            expectOrder(order === "ascending" ? ["M1", "M2"] : ["M2", "M1"])
        })
    }
}
