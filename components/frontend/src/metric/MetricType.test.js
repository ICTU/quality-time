import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricType } from './MetricType';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const data_model = {
    subjects: {
        subject_type: {
            metrics: ["violations", "source_version"]
        }
    },
    metrics: {
        violations: { unit: "violations", direction: "<", name: "Violations", default_scale: "count", scales: ["count", "percentage"] },
        source_version: { unit: "", direction: "<", name: "Source version", default_scale: "version_number", scales: ["version_number"] }
    }
};

function render_metric_type() {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={data_model}>
                <MetricType
                    subjectType="subject_type"
                    metricType="violations"
                    metric_uuid="metric_uuid"
                    reload={() => {/* Dummy implementation */ }}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('sets the metric type', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_type() });
    await userEvent.type(screen.getByRole("combobox"), 'Source version{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/type", { type: "source_version" });
});