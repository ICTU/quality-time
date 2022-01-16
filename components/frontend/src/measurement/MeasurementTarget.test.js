import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { MeasurementTarget } from './MeasurementTarget';

it('renders the target with unit', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations" }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/≦ 0 violations/).length).toBe(1)
})

it('renders the target with minutes', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { direction: "<", unit: "minutes" } } }}>
            <MeasurementTarget metric={{ type: "duration" }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/≦ 0:00 hours/).length).toBe(1)
})

it('renders the target with minutes percentage', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { direction: "<", unit: "minutes" } } }}>
            <MeasurementTarget metric={{ type: "duration", scale: "percentage" }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/≦ 0% minutes/).length).toBe(1)
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