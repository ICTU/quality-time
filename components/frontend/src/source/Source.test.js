import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Source } from './Source';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const datamodel = {
    metrics: { metric_type: { sources: ["source_type1", "source_type2"] }, unsupported_metric: { sources: [] } },
    sources: {
        source_type1: { name: "Source type 1", parameters: {} },
        source_type2: { name: "Source type 2", parameters: {} }
    }
};
const source = { type: "source_type1" };
const metric = { type: "metric_type", sources: { "source_uuid": source } }
const report = { report_uuid: "report_uuid", subjects: {} };

function render_source(metric, props) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Source
                    metric={metric}
                    report={report}
                    source_uuid="source_uuid"
                    {...props}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    )
}

it('invokes the callback on clicking delete', () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    render_source(metric);
    fireEvent.click(screen.getByText(/Delete source/));
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "delete", "source/source_uuid", {});
});

it('changes the source type', () => {
    render_source(metric);
    fireEvent.click(screen.getAllByText(/Source type 1/)[0]);
    fireEvent.click(screen.getByText(/Source type 2/));
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/attribute/type", { type: "source_type2" });
});

it('changes the source name', async () => {
    render_source(metric);
    await userEvent.type(screen.getByLabelText(/Source name/), 'New source name{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/attribute/name", { name: "New source name" });
});

it('shows a connection error message', () => {
    render_source(metric, { measurement_source: { connection_error: "Oops" } });
    expect(screen.getAllByText(/Connection error/).length).toBe(1);
});

it('shows a parse error message', () => {
    render_source(metric, { measurement_source: { parse_error: "Oops" } });
    expect(screen.getAllByText(/Parse error/).length).toBe(1);
});

it('shows a config error message', () => {
    render_source({ type: "unsupported_metric", sources: { "source_uuid": source } });
    expect(screen.getAllByText(/Configuration error/).length).toBe(1);
});

it('loads the changelog', async () => {
    render_source(metric);
    await act(async () => { fireEvent.click(screen.getByText(/Changelog/)); });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/source/source_uuid/5");
});
