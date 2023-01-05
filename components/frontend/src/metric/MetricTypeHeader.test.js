import React from 'react';
import { render, screen } from '@testing-library/react';
import { MetricTypeHeader } from "./MetricTypeHeader";

function renderMetricTypeHeader() {
    render(
        <MetricTypeHeader
            metricType={
                {
                    name: "Metric type",
                    description: "Description",
                }
            }
        />
    );
}

it('shows the header', async () => {
    renderMetricTypeHeader();
    expect(screen.getAllByText("Metric type").length).toBe(1)
});
