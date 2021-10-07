import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { SourceStatus } from './SourceStatus';
import { DataModel } from '../context/Contexts';

const metric = { sources: { source_uuid: { name: "Source name" } } };

function render_source_status(measurement_source) {
    return render(
        <DataModel.Provider value={{}}>
            <SourceStatus metric={metric} measurement_source={measurement_source} />
        </DataModel.Provider>
    )
}

it('renders the hyperlink label if the the source has a landing url', () => {
    render_source_status({ landing_url: "https://landing", source_uuid: "source_uuid" });
    expect(screen.getAllByRole("link").length).toBe(1)
});

it('renders the source label if there is no error', () => {
    render_source_status({source_uuid: "source_uuid"});
    expect(screen.getAllByText(/Source name/).length).toBe(1)
});

it('renders the source label and the popup if there is an connection error', async () => {
    render_source_status({source_uuid: "source_uuid", connection_error: "error" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(() => {
        expect(screen.queryByText("Connection error")).not.toBe(null)
    })
});

it('renders the source label and the popup if there is a parse error', async () => {
    render_source_status({source_uuid: "source_uuid", parse_error: "error" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(() => {
        expect(screen.queryByText("Parse error")).not.toBe(null)
    })
});

it('renders nothing if the source has been deleted', () => {
    render_source_status({source_uuid: "other_source_uuid"});
    expect(screen.queryByText(/Source name/)).toBe(null)
});
