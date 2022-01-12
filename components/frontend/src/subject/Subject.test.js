import { act, render, screen } from "@testing-library/react";
import { Subject } from "./Subject";
import * as fetch_server_api from '../api/fetch_server_api';
import { DataModel } from "../context/DataModel";
import { datamodel, report } from "../__fixtures__/fixtures";

function renderSubject(trend) {
    render(
        <DataModel.Provider value={datamodel}>
            <Subject
                report={report}
                subject_uuid="subject_uuid"
                tags={[]}
                hiddenColumns={[]}
                subjectTrendTable={trend}
                visibleDetailsTabs={[]} />
        </DataModel.Provider>
    )
}

it('fetches measurements', async () => {
    jest.mock("../api/fetch_server_api.js")
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, measurements: [] });
    await act(async () => { renderSubject(true) });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "subject/subject_uuid/measurements", undefined);
})

it('shows the subject title', async () => {
    await act(async () => { renderSubject(true) });
    expect(screen.queryAllByText("Subject 1 title").length).toBe(1);
})
