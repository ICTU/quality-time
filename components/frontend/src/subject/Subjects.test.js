import React from 'react';
import { act, fireEvent, render, screen } from "@testing-library/react";
import { createMemoryHistory } from 'history';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Subjects } from './Subjects';
import { datamodel, report } from "../__fixtures__/fixtures";
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

jest.mock('../widgets/menu_options', () => {
    const originalModule = jest.requireActual('../api/subject');

    //Mock the default export and named export 'foo'
    return {
        __esModule: true,
        ...originalModule,
        subject_options: jest.fn(() => [{key: "1", text: "dummy option 1"}, {key: "2", text: "dummy option 2"}]),
    };
});

beforeEach(() => {
    jest.clearAllMocks();
});

function renderSubjects(permissions = [], initialEntries = []) {
    let history
    if (initialEntries.length > 0) {
        history = createMemoryHistory({ initialEntries: initialEntries })
    } else {
        history = createMemoryHistory()
    }
    return render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={datamodel}>
                <Subjects
                    hiddenColumns={[]}
                    history={history}
                    report={report}
                    reports={[report]}
                    tags={[]}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    )
}

it("shows the subjects", () => {
    renderSubjects();
    expect(screen.getAllByText(/Subject/).length).toBe(2);
})

it("shows the add subject button when editable", () => {
    renderSubjects([EDIT_REPORT_PERMISSION]);
    expect(screen.getAllByText(/Add subject/).length).toBe(1);
})

it("does not show the add subject button when not editable", () => {
    renderSubjects();
    expect(screen.queryByText(/Add subject/)).toBeNull();
})

it("adds a subject", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([EDIT_REPORT_PERMISSION]);
    await act(async () => fireEvent.click(screen.getByText(/Add subject/)))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/new/undefined", { });
});

it("copies a subject", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([EDIT_REPORT_PERMISSION]);
    await act(async () => fireEvent.click(screen.getByText("Copy subject")))
    await act(async () => fireEvent.click(screen.getByText("dummy option 1")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/copy/undefined", { });
});

it("moves a subject", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Move subject")))
    await act(async () => fireEvent.click(screen.getByText("dummy option 2")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/move/undefined", { });
});

it("hides metrics not requiring action", () => {
    renderSubjects();
    expect(screen.getAllByText(/Hide metrics not requiring action/).length).toBe(2)
    fireEvent.click(screen.getAllByText(/Hide metrics not requiring action/)[0]);
    expect(screen.queryAllByText(/Hide metrics not requiring action/).length).toBe(0)
    fireEvent.click(screen.getAllByText(/Show all metrics/)[0]);
    expect(screen.getAllByText(/Hide metrics not requiring action/).length).toBe(2)
})

it('sorts the metrics by name', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
})

it('sorts the metrics by status', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by measurement value', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Measurement/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Measurement/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by target value', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Target/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Target/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by source', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Source/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Source/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by comment', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Comment/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Comment/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by issues', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Issues/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Issues/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by tags', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Tags/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Tags/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('sorts the metrics by unit', () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([], ["?subject_trend_table=true"]);
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Unit/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Unit/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('keeps sort direction when sorting another column', () => {
    renderSubjects();
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
    fireEvent.click(screen.getAllByText(/Status/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})

it('stops sorting when add metric is clicked', async () => {
    renderSubjects([EDIT_REPORT_PERMISSION]);
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
    await act(async () => fireEvent.click(screen.getAllByText(/Add metric/)[0]))
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
})

it('stops sorting when metrics are reordered', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([EDIT_REPORT_PERMISSION]);
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M1", "M2"])
    fireEvent.click(screen.getAllByText(/Metric/)[0])
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
    await act(async () => fireEvent.click(screen.getAllByTitle(/expand/)[1]))
    await act(async () => fireEvent.click(screen.getAllByRole("button", {text: "Move metric to the last row"})[0]))
    expect(screen.queryAllByText(/M[12]/).map((element) => element.innerHTML)).toMatchObject(["M2", "M1"])
})
