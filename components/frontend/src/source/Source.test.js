import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Source } from './Source';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const datamodel = {
    metrics: { metric_type: { sources: ["source_type1", "source_type2"] } },
    sources: { 
        source_type1: { name: "Source type 1", parameters: {} },
        source_type2: { name: "Source type 2", parameters: {} }
    }
};
const source = { type: "source_type1" };
const report = { report_uuid: "report_uuid", subjects: {} };

function render_source() {
    render(
        <ReadOnlyContext.Provider value={false}>
            <Source 
                datamodel={datamodel} 
                metric_type="metric_type" 
                report={report} 
                reports={[report]} 
                source={source} 
                source_uuid="source_uuid" 
            />
        </ReadOnlyContext.Provider>
    )
}

it('invokes the callback on clicking delete', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_source();
        fireEvent.click(screen.getByText(/Delete source/));
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "delete", "source/source_uuid", {});
});

it('changes the source type', async () => {
    await act(async () => {
        render_source();
        fireEvent.click(screen.getAllByText(/Source type 1/)[0]);
    })
    fireEvent.click(screen.getByText(/Source type 2/));
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/attribute/type", {type: "source_type2"});
});

it('changes the source name', async () => {
    await act(async () => {
        render_source();
    })
    userEvent.type(screen.getByLabelText(/Source name/), 'New source name{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/attribute/name", {name: "New source name"});
});
