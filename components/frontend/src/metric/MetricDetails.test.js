import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricDetails } from './MetricDetails';
import * as changelog_api from '../api/changelog';
import * as metric_api from '../api/metric';
import * as measurement_api from '../api/measurement';

jest.mock("../api/changelog.js");
jest.mock("../api/metric.js");
jest.mock("../api/measurement.js");

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Metric",
            metrics: {
                metric_uuid: {
                    accept_debt: false,
                    tags: [],
                    type: "violations",
                    sources: {
                        source_uuid: {
                            type: "source_type",
                            entities: []
                        }
                    }
                },
                metric_uuid2: {}
            }
        }
    }
};

const data_model = {
    sources: { source_type: { name: "The source", parameters: {}, entities: { violations: { name: "Attribute", attributes: []} } } },
    metrics: { violations: { direction: "<", tags: [], sources: ["source_type"] } }
}

async function render_metric_details(stop_sort, connection_error) {
    measurement_api.get_measurements.mockImplementation(() => Promise.resolve({
        ok: true,
        measurements: [
            {
                count: { value: "42" }, start: "2020-02-29T10:25:52.252Z", end: "2020-02-29T11:25:52.252Z",
                sources: [
                    {},
                    { source_uuid: "source_uuid" },
                    { source_uuid: "source_uuid", entities: [{key: "1"}], connection_error: connection_error }
                ]
            },
        ]
    }));
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));

    await act(async () => {
        render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={data_model}>
                    <MetricDetails
                        metric_uuid="metric_uuid"
                        report={report}
                        reports={[report]}
                        stop_sort={stop_sort}
                        subject_uuid="subject_uuid"
                        visibleDetailsTabs={[]}
                        toggleVisibleDetailsTab={() => {/*Dummy implementation*/ }}
                    />
                </DataModel.Provider>
            </Permissions.Provider>
        )
    })
}

it('switches tabs', async () => {
    await render_metric_details();
    expect(screen.getAllByText(/Metric name/).length).toBe(1);
    await act(async () => fireEvent.click(screen.getByText(/Sources/)))
    expect(screen.getAllByText(/Source name/).length).toBe(1);
});

it('switches tabs to measurement entities', async () => {
    await render_metric_details();
    expect(screen.getAllByText(/Metric name/).length).toBe(1);
    await act(async () => fireEvent.click(screen.getByText(/The source/)))
    expect(screen.getAllByText(/Attribute status/).length).toBe(1);
})

it('switches tabs to the trend graph', async () => {
    await render_metric_details();
    expect(screen.getAllByText(/Metric name/).length).toBe(1);
    await act(async () => fireEvent.click(screen.getByText(/Trend graph/)))
    expect(screen.getAllByText(/Time/).length).toBe(1);
})

it('displays whether sources have errors', async () => {
    await render_metric_details(null, "Connection error");
    expect(screen.getByText(/Sources/)).toHaveClass("red label");
});

it('calls the callback on click', async () => {
    const mockCallback = jest.fn();
    await render_metric_details(mockCallback);
    await act(async () => fireEvent.click(screen.getByLabelText(/Move metric to the last row/)));
    expect(mockCallback).toHaveBeenCalled();
    expect(measurement_api.get_measurements).toHaveBeenCalled();
})

it('loads the changelog', async () => {
    await render_metric_details();
    await act(async () => fireEvent.click(screen.getByText(/Changelog/)));
    expect(changelog_api.get_changelog).toHaveBeenCalledWith(5, { metric_uuid: "metric_uuid" });
});

it('calls the callback on delete', async () => {
    await render_metric_details();
    await act(async () => fireEvent.click(screen.getByText(/Delete metric/)));
    expect(metric_api.delete_metric).toHaveBeenCalled();
})
