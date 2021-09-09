import React from 'react';
import { render, screen } from '@testing-library/react';
import { MetricParameters } from './MetricParameters';

const data_model = {
    metrics: {
        violations: { unit: "violation", direction: "<", name: "Violations", default_scale: "count", scales: ["count", "percentage"] },
        source_version: { unit: "", direction: "<", name: "Source version", default_scale: "version_number", scales: ["version_number"] }
    }
};

const report = { summary_by_tag: {} }

it('renders the default metric name', () => {
    render(<MetricParameters
        datamodel={data_model} report={report}
        metric={{ type: "violations", tags: [], accept_debt: false }}
        metric_uuid="metric_uuid"
    />);
    expect(screen.getAllByPlaceholderText(/Violations/).length).toBe(1);
});

it('shows the metric unit field for metrics with the count scale', () => {
    render(<MetricParameters
        datamodel={data_model} report={report}
        metric={{ type: "violations", tags: [], accept_debt: false }}
        metric_uuid="metric_uuid"
    />);
    expect(screen.getAllByText(/Metric unit/).length).toBe(1);
});

it('shows the metric unit field for metrics with the percentage scale', () => {
    render(<MetricParameters
        datamodel={data_model} report={report}
        metric={{ type: "violations", tags: [], accept_debt: false, scale: "percentage" }}
        metric_uuid="metric_uuid"
    />);
    expect(screen.getAllByText(/Metric unit/).length).toBe(1);
});

it('skips the metric unit field for metrics with the version number scale', () => {
    render(<MetricParameters
        datamodel={data_model} report={report}
        metric={{ type: "source_version", tags: [], accept_debt: false }}
        metric_uuid="metric_uuid"
    />);
    expect(screen.queryAllByText(/Metric unit/).length).toBe(0);
});