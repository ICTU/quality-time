import React from 'react';
import { render, screen } from '@testing-library/react';
import { Overrun } from './Overrun';

const dates = [new Date("2020-01-01"), new Date("2020-12-31")]

it("renders nothing if there is no overrun", () => {
    render(<Overrun measurements={[]} dates={dates} />)
    expect(screen.queryAllByDisplayValue(/days/).length).toBe(0)
})

it("renders the days overrun if the metric has overrun its deadline", () => {
    render(
        <Overrun
            dates={dates}
            metric_uuid="uuid"
            measurements={[{metric_uuid: "uuid", start: "2020-01-01", end: "2020-12-31"}]}
        />
    )
    expect(screen.queryAllByText(/days/).length).toBe(1)
})

it("merges the days overrun if the metric has consecutive measurements", () => {
    render(
        <Overrun
            dates={dates}
            metric_uuid="uuid"
            measurements={[{metric_uuid: "uuid", start: "2020-01-01", end: "2020-12-31"}]}
        />
    )
    expect(screen.queryAllByText(/days/).length).toBe(1)
})
