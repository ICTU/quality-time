import React from 'react';
import { render, screen } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { MetricSummaryCard } from './MetricSummaryCard';


function render_pie_chart({ summary = { blue: 0, red: 0, green: 0, yellow: 0, white: 0, grey: 0 }, dark = true } = {}) {
    return render(
        <DarkMode.Provider value={dark}>
            <MetricSummaryCard summary={{ "2023-01-01": summary }} />
        </DarkMode.Provider>
    )
}

const dateString = (new Date("2023-01-01")).toLocaleDateString()

it('shows there are no metrics', () => {
    render_pie_chart()
    expect(screen.getAllByLabelText(`Status on ${dateString}: no metrics.`, { exact: false }).length).toBe(1)
})

it('shows there are no metrics in dark mode', () => {
    render_pie_chart({ dark: true })
    expect(screen.getAllByLabelText(`Status on ${dateString}: no metrics`, { exact: false }).length).toBe(1)
})

it('shows the number of metrics per status', () => {
    render_pie_chart({ summary: { blue: 2, red: 1, green: 2, yellow: 3, white: 1, grey: 1 } })
    expect(screen.getAllByLabelText(`Status on ${dateString}: 10 metrics, 2 target met, 1 target not met, 3 near target, 1 with accepted technical debt, 2 informative, 1 with unknown status.`, { exact: false }).length).toBe(1)
})
