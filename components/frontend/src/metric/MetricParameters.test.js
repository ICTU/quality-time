import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricParameters } from './MetricParameters';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const data_model = {
    metrics: {
        violations: { unit: "violations", direction: "<", name: "Violations", default_scale: "count", scales: ["count", "percentage"] },
        source_version: { unit: "", direction: "<", name: "Source version", default_scale: "version_number", scales: ["version_number"] }
    }
};

const report = { summary_by_tag: {} }

function render_metric_parameters(scale = "count") {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={data_model}>
                <MetricParameters
                    metric={{ type: "violations", tags: [], accept_debt: false, scale: scale }}
                    metric_uuid="metric_uuid"
                    reload={() => {/* Dummy implementation */ }}
                    report={report}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('sets the metric name', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters() });
    userEvent.type(screen.getByLabelText(/Metric name/), '{selectall}{del}New metric name{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/name", { name: "New metric name" });
});

it('sets the metric unit for metrics with the count scale', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters() });
    userEvent.type(screen.getByLabelText(/Metric unit/), '{selectall}{del}New metric unit{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/unit", { unit: "New metric unit" });
});

it('sets the metric unit field for metrics with the percentage scale', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters("percentage") });
    userEvent.type(screen.getByLabelText(/Metric unit/), '{selectall}{del}New metric unit{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/unit", { unit: "New metric unit" });
});

it('skips the metric unit field for metrics with the version number scale', () => {
    render(<DataModel.Provider value={data_model}><MetricParameters
        report={report}
        metric={{ type: "source_version", tags: [], accept_debt: false }}
        metric_uuid="metric_uuid"
    /></DataModel.Provider>);
    expect(screen.queryAllByText(/Metric unit/).length).toBe(0);
});
