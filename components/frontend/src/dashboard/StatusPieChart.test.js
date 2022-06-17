import React from 'react';
import { render, screen } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { StatusPieChart } from './StatusPieChart';

function render_pie_chart({ blue = 0, red = 0, green = 0, yellow = 0, white = 0, grey = 0, dark = true } = {}) {
    return render(
        <DarkMode.Provider value={dark}>
            <StatusPieChart blue={blue} red={red} green={green} yellow={yellow} white={white} grey={grey} />
        </DarkMode.Provider>
    )
}

it('shows there are no metrics', () => {
    render_pie_chart()
    expect(screen.getAllByLabelText(/Status pie chart: no metrics/).length).toBe(1)
    expect(screen.getAllByText(/No/).length).toBe(1)
    expect(screen.getAllByText(/metrics/).length).toBe(1)
})

it('shows there are no metrics in dark mode', () => {
    render_pie_chart({ dark: true })
    expect(screen.getAllByLabelText(/Status pie chart: no metrics/).length).toBe(1)
    expect(screen.getAllByText(/No/).length).toBe(1)
    expect(screen.getAllByText(/metrics/).length).toBe(1)
})

it('shows the number of metrics per status', () => {
    render_pie_chart({ blue: 2, red: 1, green: 2, yellow: 3, white: 1, grey: 1 })
    expect(screen.getAllByLabelText(
        /Status pie chart: 10 metrics, 2 target met, 1 target not met, 3 near target, 1 with accepted technical debt, 2 informative, 1 with unknown status/).length).toBe(1)
})
