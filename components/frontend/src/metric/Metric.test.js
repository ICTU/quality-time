import React from 'react';
import { Table } from 'semantic-ui-react';
import { render, screen } from '@testing-library/react';
import { Metric } from './Metric';
import { DataModel } from '../context/DataModel';

let report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Subject",
            metrics: {
                violations: {
                    name: "Violations",
                    accept_debt: false,
                    tags: [],
                    type: "violations",
                    sources: {source_uuid1: {name: "Source 1"}, source_uuid2: {name: "Source 2"}},
                    status: "target_not_met",
                    value: "50",
                    latest_measurement: { sources: [{ source_uuid: "source_uuid1" }, {source_uuid: "source_uuid2"}] },
                    recent_measurements: []
                },
                stability: {
                    name: "Stability",
                    accept_debt: false,
                    tags: [],
                    type: "stability",
                    sources: {source_uuid: {name: "Source"}},
                    status: "target_not_met",
                    value: "50",
                    latest_measurement: { sources: [{ source_uuid: "source_uuid" }] },
                    recent_measurements: []
                }
            }
        }
    }
};
const data_model = {
    metrics: {
        stability: { name: "Stability", unit: "minutes", direction: "<", tags: [] },
        violations: { name: "Metric type", unit: "violations", direction: "<", tags: [] }
    }
};

function render_metric(metric_uuid) {
    return (
        render(
            <DataModel.Provider value={data_model}>
                <Table>
                    <Table.Body>
                        <Metric
                            hiddenColumns={[]}
                            report={report}
                            reports={[report]}
                            metric={report.subjects["subject_uuid"].metrics[metric_uuid]}
                            metric_uuid={metric_uuid}
                            subject_uuid="subject_uuid"
                            visibleDetailsTabs={[]} />
                    </Table.Body>
                </Table>
            </DataModel.Provider>
        )
    )
}

it('renders the metric', () => {
    render_metric("violations");
    expect(screen.getAllByText(/Violations/).length).toBe(1);
    expect(screen.getAllByText(/50 violations/).length).toBe(1);
    expect(screen.getAllByText(/≦ 0 violations/).length).toBe(1);
    expect(screen.getAllByText(/Source 1, Source 2/).length).toBe(1);
});

it('renders the minutes', () => {
    render_metric("stability");
    expect(screen.getAllByText(/0:50 hours/).length).toBe(1);
    expect(screen.getAllByText(/≦ 0:00 hours/).length).toBe(1);
});

it('renders the minutes as percentage', () => {
    report.subjects.subject_uuid.metrics.stability.scale = "percentage";
    render_metric("stability");
    expect(screen.getAllByText(/50% minutes/).length).toBe(1);
    expect(screen.getAllByText(/≦ 0% minutes/).length).toBe(1);
});
