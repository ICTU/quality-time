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
                    dates={[]}
                    hiddenColumns={[]}
                    history={history}
                    report={report}
                    reports={[report]}
                    tags={[]}
                    visibleDetailsTabs={[]}
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
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/new/report_uuid", { });
});

it("copies a subject", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([EDIT_REPORT_PERMISSION]);
    await act(async () => fireEvent.click(screen.getByText("Copy subject")))
    await act(async () => fireEvent.click(screen.getByText("dummy option 1")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/copy/report_uuid", { });
});

it("moves a subject", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    renderSubjects([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Move subject")))
    await act(async () => fireEvent.click(screen.getByText("dummy option 2")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/move/report_uuid", { });
});
