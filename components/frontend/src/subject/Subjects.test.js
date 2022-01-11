import React from 'react';
import { act, fireEvent, render, screen } from "@testing-library/react";
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Subjects } from './Subjects';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { datamodel, report } from "../__fixtures__/fixtures";

jest.mock('../api/subject', () => {
    const originalModule = jest.requireActual('../api/subject');

    //Mock the default export and named export 'foo'
    return {
        __esModule: true,
        ...originalModule,
        add_subject: jest.fn(),
        copy_subject: jest.fn(),
        move_subject: jest.fn(),
    };
});

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

function renderSubjects(permissions = []) {
    return render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={datamodel}>
                <Subjects
                    hiddenColumns={[]}
                    history={{ location: {}, replace: () => {/* Dummy implementation */ } }}
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
    renderSubjects([EDIT_REPORT_PERMISSION]);
    await act(async () => fireEvent.click(screen.getByText(/Add subject/)))
    expect(add_subject.mock.calls.length).toBe(1);
});

it("copies a subject", async () => {
    renderSubjects([EDIT_REPORT_PERMISSION]);
    await act(async () => fireEvent.click(screen.getByText("Copy subject")))
    expect(subject_options.mock.calls.length).toBe(1);
    await act(async () => fireEvent.click(screen.getByText("dummy option 1")))
    expect(copy_subject.mock.calls.length).toBe(1)
});

it("moves a subject", async () => {
    renderSubjects([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Move subject")))
    expect(subject_options.mock.calls.length).toBe(1);
    await act(async () => fireEvent.click(screen.getByText("dummy option 2")))
    expect(move_subject.mock.calls.length).toBe(1)
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
