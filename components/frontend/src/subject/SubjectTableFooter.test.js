import { act, fireEvent, render, screen } from "@testing-library/react";
import { Table } from "semantic-ui-react";
import { DataModel } from "../context/DataModel";
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions";
import * as fetch_server_api from '../api/fetch_server_api';
import { datamodel, report } from "../__fixtures__/fixtures";
import { SubjectTableFooter } from "./SubjectTableFooter";

const stopSorting = jest.fn()

jest.mock("../api/fetch_server_api.js")
fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });

it('shows the add metric button and adds a metric when clicked', () => {
    const { getByText } = render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Table>
                    <SubjectTableFooter
                        subjectUuid="subject_uuid"
                        subject={report.subjects.subject_uuid}
                        stopSorting={stopSorting} />
                </Table>
            </DataModel.Provider>
        </Permissions.Provider>
    );
    fireEvent.click(getByText(/Add metric/))
    fireEvent.click(screen.getByText(/Metric type/));
    expect(stopSorting).toBeCalled()
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/new/subject_uuid", { type: "metric_type" });
});

it('copies a metric when the copy button is clicked and a metric is selected', async () => {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Table>
                    <SubjectTableFooter
                        subjectUuid="subject_uuid"
                        subject={report.subjects.subject_uuid}
                        reports={[report]}
                        stopSorting={stopSorting} />
                </Table>
            </DataModel.Provider>
        </Permissions.Provider>);
    fireEvent.click(screen.getByText(/Copy metric/));
    await act(async () => { fireEvent.click(screen.getAllByText(/M1/)[0]); });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid/copy/subject_uuid", {});
});

it('moves a metric when the move button is clicked and a metric is selected', async () => {
    render(
        <DataModel.Provider value={datamodel}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <Table>
                    <SubjectTableFooter
                        subjectUuid="subject_uuid"
                        subject={report.subjects.subject_uuid}
                        reports={[report]}
                        stopSorting={stopSorting} />
                </Table>
            </Permissions.Provider>
        </DataModel.Provider>)
    fireEvent.click(screen.getByText(/Move metric/));
    await act(async () => { fireEvent.click(screen.getByText(/Subject 2 title/)); })
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid3/move/subject_uuid", {});
});
