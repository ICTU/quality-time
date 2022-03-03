import React from 'react';
import { render, screen } from '@testing-library/react';
import { TrendSparkline } from './TrendSparkline';
import { DarkMode } from '../context/DarkMode';

it('returns null when the metric scale is version number', () => {
    render(<TrendSparkline scale="version_number"/>)
    expect(screen.queryAllByLabelText(/sparkline graph/).length).toBe(0)
})

it('renders an empty sparkline if there are no measurements', () => {
    render(<TrendSparkline measurements={[]} />)
    expect(screen.queryAllByLabelText(/sparkline graph showing 0 different measurement values/).length).toBe(1)
});

it('renders an empty sparkline if there are no measurements in dark mode', () => {
    render(<DarkMode.Provider value="true"><TrendSparkline measurements={[]} /></DarkMode.Provider>)
    expect(screen.queryAllByLabelText(/sparkline graph showing 0 different measurement values/).length).toBe(1)
});

it('renders a recent measurement', () => {
    render(<TrendSparkline measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]} scale="count" />);
    expect(screen.queryAllByLabelText(/sparkline graph showing 1 different measurement value in the week before today/).length).toBe(1)
});

it('renders multiple recent measurements', () => {
    render(
        <TrendSparkline
            measurements={[
                { count: { value: null }, start: "2019-09-27", end: "2019-09-28" },
                { count: { value: "1" }, start: "2019-09-28", end: "2019-09-29" },
                { count: { value: "2" }, start: "2019-09-29", end: "2019-09-30" }
            ]}
            scale="count"
        />
    );
    expect(screen.queryAllByLabelText(/sparkline graph showing 2 different measurement values in the week before today/).length).toBe(1)
});

it('renders old measurements', () => {
    const date = new Date("2020-01-01");
    render(<TrendSparkline measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]} report_date={date} scale="count" />);
    expect(screen.queryAllByLabelText(`sparkline graph showing 1 different measurement value in the week before ${date.toLocaleDateString()}`).length).toBe(1)
});
