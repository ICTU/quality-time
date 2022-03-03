import React from 'react';
import { render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { TrendGraph } from './TrendGraph';
import { DarkMode } from '../context/DarkMode';

const dataModel = {
    metrics: {
        stability: { name: "Stability", unit: "minutes", direction: "<", tags: [] },
        violations: { name: "Violations", unit: "violations", direction: "<", tags: [] }
    }
};

function render_trendgraph(measurements = [], darkMode = false) {
    return (
        render(
            <DarkMode.Provider value={darkMode}>
                <DataModel.Provider value={dataModel}>
                    <TrendGraph metric={{ type: "violations", scale: "count" }} measurements={measurements} />
                </DataModel.Provider>
            </DarkMode.Provider>
        )
    )
}

it('renders the time axis', () => {
    render_trendgraph();
    expect(screen.getAllByText(/Time/).length).toBe(1);
});

it('renders the measurements', () => {
    render_trendgraph([{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]);
    expect(screen.getAllByText(/Time/).length).toBe(1);
});

it('renders the measurements in dark mode', () => {
    render_trendgraph([{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }], true);
    expect(screen.getAllByText(/Time/).length).toBe(1);
});

it('renders measurements with targets', () => {
    render_trendgraph([{ count: { value: "1", target: "10", near_target: "20" }, start: "2019-09-29", end: "2019-09-30" }]);
    expect(screen.getAllByText(/Time/).length).toBe(1);
});
