import { act, fireEvent, render, screen } from "@testing-library/react";
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

it('sorts metrics by name ascending', async () => {
    await act(async () => { renderSubject([], false, "name", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by name descending', async () => {
    await act(async () => { renderSubject([], false, "name", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by measurement ascending', async () => {
    await act(async () => { renderSubject([], false, "measurement", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by measurement descending', async () => {
    await act(async () => { renderSubject([], false, "measurement", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by target ascending', async () => {
    await act(async () => { renderSubject([], false, "target", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by target descending', async () => {
    await act(async () => { renderSubject([], false, "target", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by comment ascending', async () => {
    await act(async () => { renderSubject([], false, "comment", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by comment descending', async () => {
    await act(async () => { renderSubject([], false, "comment", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by status ascending', async () => {
    await act(async () => { renderSubject([], false, "status", "ascending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by status descending', async () => {
    await act(async () => { renderSubject([], false, "status", "descending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by source ascending', async () => {
    await act(async () => { renderSubject([], false, "source", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by source descending', async () => {
    await act(async () => { renderSubject([], false, "source", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by issues ascending', async () => {
    await act(async () => { renderSubject([], false, "issues", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by issues descending', async () => {
    await act(async () => { renderSubject([], false, "issues", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by tags ascending', async () => {
    await act(async () => { renderSubject([], false, "tags", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by tags descending', async () => {
    await act(async () => { renderSubject([], false, "tags", "descending") });
    expectOrder(["M2", "M1"])
})

it('sorts metrics by unit ascending', async () => {
    await act(async () => { renderSubject([], false, "unit", "ascending") });
    expectOrder(["M1", "M2"])
})

it('sorts metrics by unit descending', async () => {
    await act(async () => { renderSubject([], false, "unit", "descending") });
    expectOrder(["M2", "M1"])
})
