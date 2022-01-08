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
        source_type1: { name: "Source type 1", parameters: {} },
        source_type2: { name: "Source type 2", parameters: {} }
    }
};

const reports = [
    {
        subjects: {
            subject_uuid: {
                name: "Subject",
                metrics: {
                    metric_uuid: {
                        name: "Metric",
                        sources: { source_uuid: { name: "Source 1", type: "source_type1" } }
                    },
                    other_metric_uuid: {
                        name: "Other metric",
                        sources: { other_source_uuid: { name: "Source 2", type: "source_type2" } }
                    }
                }
            }
        }
    }
]

function render_sources(props) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Sources {...props} />
            </DataModel.Provider>
        </Permissions.Provider>
    )
}

it('shows a message if there are no sources', () => {
    render_sources({ metric: { type: "metric_type", sources: {} } });
    expect(screen.getAllByText(/No sources have been configured/).length).toBe(1);
})

it('shows a source', () => {
    render_sources({ metric: { type: "metric_type", sources: { source_uuid: { type: "source_type1" } } } })
    expect(screen.getAllByPlaceholderText(/Source type 1/).length).toBe(1);
})

it("doesn't show sources not in the data model", () => {
    render_sources(
        {
            metric: {
                type: "metric_type",
                sources: {
                    other_uuid: { name: "Other source", type: "non-existing" },
                    source_uuid: { name: "Source of type 1", type: "source_type1" }
                }
            }
        }
    )
    expect(screen.queryAllByDisplayValue(/Source of type 1/).length).toBe(1);
    expect(screen.queryAllByDisplayValue(/Other source/).length).toBe(0);
})

it('shows errored sources', () => {
    render_sources(
        {
            metric: { type: "metric_type", sources: { source_uuid: { type: "source_type1" } } },
            measurement: {sources: [{source_uuid: "source_uuid", connection_error: "Oops"}]}
        }
    )
    expect(screen.getAllByText(/Connection error/).length).toBe(1);
})

it('creates a new source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_sources(
            {
                metric_uuid: "metric_uuid",
                metric: { type: "metric_type", sources: { source_uuid: { type: "source_type1" } } }
            }
        )
        fireEvent.click(screen.getByText(/Add source/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/new/metric_uuid", {});
})

it('copies a source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_sources(
            {
                metric_uuid: "metric_uuid",
                metric: { type: "metric_type", sources: { source_uuid: { type: "source_type1" } } },
                reports: reports
            }
        )
        fireEvent.click(screen.getByText(/Copy source/))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Source 1/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/source_uuid/copy/metric_uuid", {});
})

it('moves a source', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_sources(
            {
                metric_uuid: "metric_uuid",
                metric: { type: "metric_type", sources: { source_uuid: { type: "source_type1" } } },
                reports: reports
            }
        )
        fireEvent.click(screen.getByText(/Move source/))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Source 2/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/other_source_uuid/move/metric_uuid", {});
})

it('updates a parameter of a source', async () => {
    const metric = { type: "metric_type", sources: { source_uuid: { name: "Source 1", type: "source_type1", parameters: {url: "https://test.nl" } } } }
    reports[0].subjects.subject_uuid.metrics.metric_uuid = metric
    dataModel.sources.source_type1.parameters = {url: {type: "url", metrics: ["metric_type"]}}
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, nr_sources_mass_edited: 2 });
    render_sources(
        {
            metric_uuid: "metric_uuid",
            metric: metric,
            reports: reports,
            report: reports[0],
            reload: () => {/* Dummy implemention */ }
        }
    )
    userEvent.type(screen.getByDisplayValue(/http:\/\/test.nl/), '{selectall}some other url{enter}')
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue('Source 1'))
    })
    expect(screen.getAllByDisplayValue('some other url').length).toBe(1)
    expect(toast.show_message).toHaveBeenCalledTimes(1)
})
