import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricDetails } from './MetricDetails';
import * as changelog_api from '../api/changelog';
import * as metric_api from '../api/metric';
import * as measurement_api from '../api/measurement';

jest.mock("../api/changelog.js");
jest.mock("../api/metric.js");
jest.mock("../api/measurement.js");
measurement_api.get_measurements.mockImplementation(() => Promise.resolve({
    ok: true,
    measurements: [
        { count: { value: "42" }, start: "2020-02-29T10:25:52.252Z", end: "2020-02-29T11:25:52.252Z", sources: [{}] },
        { count: { value: "42" }, start: "2020-02-29T10:25:52.252Z", end: "2020-02-29T11:25:52.252Z", sources: [{source_uuid: "source_uuid"}] },
        { count: { value: "42" }, start: "2020-02-29T10:25:52.252Z", end: "2020-02-29T11:25:52.252Z", sources: [{source_uuid: "source_uuid", entities: [{}]}] }
    ]
}));
changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));

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
    sources: { source_type: { parameters: {} } },
    metrics: { violations: { direction: "<", tags: [], sources: ["source_type"] } }
}

it('switches tabs', async () => {
    await act(async () => render(<Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
        <MetricDetails
            datamodel={data_model}
            metric_uuid="metric_uuid"
            report={report}
            reports={[report]}
            scale="count"
            subject_uuid="subject_uuid"
            unit="unit"
            visibleDetailsTabs={[]}
            toggleVisibleDetailsTab={() => {/*Dummy implementation*/}}
        />
    </Permissions.Provider>))
    expect(screen.getAllByText(/Metric name/).length).toBe(1);
    await act(async () => fireEvent.click(screen.getByText(/Sources/)))
    expect(screen.getAllByText(/Source name/).length).toBe(1);
})

it('calls the callback on click', async () => {
    const mockCallBack = jest.fn();
    await act(async () => {
        render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <MetricDetails
                    datamodel={data_model}
                    metric_uuid="metric_uuid"
                    report={report}
                    reports={[report]}
                    stop_sort={mockCallBack}
                    subject_uuid="subject_uuid"
                    visibleDetailsTabs={[]}
                    toggleVisibleDetailsTab={() => {/*Dummy implementation*/}}
                />
            </Permissions.Provider>
        );
    });
    await act(async () => fireEvent.click(screen.getByLabelText(/Move metric to the last row/)));
    expect(mockCallBack).toHaveBeenCalled();
    expect(measurement_api.get_measurements).toHaveBeenCalled();
})

it('calls the callback on delete', async () => {
    await act(async () => {
        render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <MetricDetails
                    datamodel={data_model}
                    metric_uuid="metric_uuid"
                    report={report}
                    reports={[report]}
                    subject_uuid="subject_uuid"
                    visibleDetailsTabs={[]}
                />
            </Permissions.Provider>
        );
    });
    await act(async () => fireEvent.click(screen.getByText(/Delete metric/)));
    expect(metric_api.delete_metric).toHaveBeenCalled();
})
