import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MetricTypeHeader } from "./MetricTypeHeader";

function renderMetricTypeHeader(rationale, rationaleUrls, explanation, explanationUrls) {
    render(
        <MetricTypeHeader
            metricType={
                {
                    name: "Metric type",
                    description: "Description",
                    rationale: rationale,
                    rationale_urls: rationaleUrls,
                    explanation: explanation,
                    explanation_urls: explanationUrls
                }
            }
        />
    );
}

it('shows the header', async () => {
    renderMetricTypeHeader();
    expect(screen.getAllByText("Metric type").length).toBe(1)
});

it('shows the rationale', async () => {
    renderMetricTypeHeader("Rationale");
    await userEvent.hover(screen.queryByRole("tooltip"))
    await waitFor(() => { expect(screen.queryAllByText(/Rationale/).length).toBe(1) });
});

it('shows the rationale URLs', async () => {
    renderMetricTypeHeader("Rationale", ["https://rationale"]);
    await userEvent.hover(screen.queryByRole("tooltip"))
    await waitFor(() => { expect(screen.queryAllByText(/https:\/\/rationale/).length).toBe(1) });
});

it('shows the explanation', async () => {
    renderMetricTypeHeader("", [], "Explanation.");
    await userEvent.hover(screen.queryByRole("tooltip"))
    await waitFor(() => { expect(screen.queryAllByText(/Explanation/).length).toBe(1) });
});

it('shows the explanation URLs', async () => {
    renderMetricTypeHeader("", [], "Explanation.", ["https://explanation"]);
    await userEvent.hover(screen.queryByRole("tooltip"))
    await waitFor(() => { expect(screen.queryAllByText(/https:\/\/explanation/).length).toBe(1) });
});
