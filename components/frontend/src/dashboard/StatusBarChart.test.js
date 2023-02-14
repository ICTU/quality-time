import React from 'react';
import { render, screen } from '@testing-library/react';
import { StatusBarChart } from './StatusBarChart';

function render_bar_chart() {
    const summary = { date1: {blue: 0, red: 0, green: 0, yellow: 0, white:0, grey: 0}}
    return render(
        <StatusBarChart summary={summary} may={10} />
    )
}

it('shows the number of metrics per status', () => {
    render_bar_chart()
    expect(screen.queryAllByLabelText(/No text/).length).toBe(0)
})
