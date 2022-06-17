import React from 'react';
import { render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { MeasurementTarget } from './MeasurementTarget';

it('renders the target', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations" }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/≦ 0/).length).toBe(1)
})

it('does not render the target if the metric is informative', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", evaluate_targets: false }} />
        </DataModel.Provider>
    )
    expect(screen.queryAllByText(/≦ 0/).length).toBe(0)
})

it('renders the target with minutes', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { direction: "<", unit: "minutes" } } }}>
            <MeasurementTarget metric={{ type: "duration" }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/≦ 0/).length).toBe(1)
})

it('renders the target with minutes percentage', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { direction: "<", unit: "minutes" } } }}>
            <MeasurementTarget metric={{ type: "duration", scale: "percentage" }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/≦ 0%/).length).toBe(1)
})

it('does not render the technical debt end date if technical debt is not accepted', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", debt_end_date: "2022-12-31" }} />
        </DataModel.Provider>
    )
    expect(screen.queryAllByText(/until /).length).toBe(0)
})

it('renders the technical debt end date if technical debt is accepted', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", accept_debt: true, debt_end_date: "2022-12-31" }} />
        </DataModel.Provider>
    )
    expect(screen.queryAllByText(/until /).length).toBe(1)
})
