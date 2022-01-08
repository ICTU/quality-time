import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Sources } from './Sources';
import * as fetch_server_api from '../api/fetch_server_api';
import * as toast from '../widgets/toast';

jest.mock("../api/fetch_server_api.js")
jest.mock("../widgets/toast.js")

const dataModel = {
    metrics: { metric_type: { sources: ["source_type1", "source_type2"] } },
    sources: {
        source_type1: { name: "Source type 1", parameters: { url: { type: "url", metrics: ["metric_type"] } } },
        source_type2: { name: "Source type 2", parameters: {} }
    }
};

const report = {
    subjects: {
        subject_uuid: {
            name: "Subject",
            metrics: {
                metric_uuid: {
                    name: "Metric",
                    type: "metric_type",
                    sources: {
                        source_uuid: { name: "Source 1", type: "source_type1", parameters: { url: "https://test.nl" } },
                        non_existing_source_type: { name: "Source with non-existing source type", type: "non-existing" },
                    }
                },
                other_metric_uuid: {
                    name: "Other metric",
                    type: "metric_type",
                    sources: { other_source_uuid: { name: "Source 2", type: "source_type2" } }
                },
                metric_without_sources: {
                    name: "Metric without sources",
                    type: "metric_type",
                    sources: {}
                }
            }
        }
    }
}

function render_sources(props) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Sources
                    report={report}
                    reports={[report]}
                    metric={report.subjects.subject_uuid.metrics.metric_uuid}
                    metric_uuid="metric_uuid"
                    measurement={{ sources: [{ source_uuid: "source_uuid", connection_error: "Oops" }] }}
                    reload={() => {/* Dummy implemention */ }}
                    {...props} />
            </DataModel.Provider>
        </Permissions.Provider>
    )
}

it('shows a source', () => {
    render_sources()
    expect(screen.getAllByPlaceholderText(/Source type 1/).length).toBe(1);
})

it('shows a message if there are no sources', () => {
    render_sources({ metric: report.subjects.subject_uuid.metrics.metric_without_sources, });
    expect(screen.getAllByText(/No sources have been configured/).length).toBe(1);
})

it("doesn't show sources not in the data model", () => {
    render_sources()
    expect(screen.queryAllByDisplayValue(/Source 1/).length).toBe(1);
    expect(screen.queryAllByDisplayValue(/Source with non-existing source type/).length).toBe(0);
})

it('shows errored sources', () => {
    render_sources()
    expect(screen.getAllByText(/Connection error/).length).toBe(1);
})

it('creates a new source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    render_sources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add source/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/new/metric_uuid", {});
})

it('copies a source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    render_sources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Copy source/))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Source 1/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/source_uuid/copy/metric_uuid", {});
})

it('moves a source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    render_sources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Move source/))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Source 2/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/other_source_uuid/move/metric_uuid", {});
})

it('updates a parameter of a source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, nr_sources_mass_edited: 0 });
    render_sources()
    userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), '{selectall}https://other{enter}')
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue('Source 1'))
    })
    expect(screen.getAllByDisplayValue('https://other').length).toBe(1)
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "source/source_uuid/parameter/url", { edit_scope: "source", url: "https://other" });
    expect(toast.show_message).toHaveBeenCalledTimes(0)
})

it('mass updates a parameter of a source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, nr_sources_mass_edited: 2 });
    render_sources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Apply change to subject/))
    })
    expect(screen.getAllByText(/Apply change to subject/).length).toBe(2)
    userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), '{selectall}https://other{enter}')
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue('Source 1'))
    })
    expect(screen.getAllByDisplayValue('https://other').length).toBe(1)
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "source/source_uuid/parameter/url", { edit_scope: "subject", url: "https://other" });
    expect(toast.show_message).toHaveBeenCalledTimes(1)
    expect(screen.getAllByText(/Apply change to subject/).length).toBe(1)
})
