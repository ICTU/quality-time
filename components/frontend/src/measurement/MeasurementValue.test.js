import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { MeasurementValue } from './MeasurementValue';

it('renders the value', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue metric={{ type: "violations", scale: "count", unit: null, latest_measurement: { count: { value: "42" } } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it('renders an unkown value', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue metric={{ type: "violations", scale: "count", unit: null, latest_measurement: { count: { value: null } } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/\?/).length).toBe(1)
})

it('renders a value that has not been measured yet', () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue metric={{ type: "violations", scale: "count", unit: null, latest_measurement: { } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/\?/).length).toBe(1)
})

it('renders a minutes value', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { unit: "minutes" } } }}>
            <MeasurementValue metric={{ type: "duration", scale: "count", unit: null, latest_measurement: { count: { value: "42" } } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/0:42/).length).toBe(1)
})

it('renders an unknown minutes value', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { unit: "minutes" } } }}>
            <MeasurementValue metric={{ type: "duration", scale: "count", unit: null, latest_measurement: { count: { value: null } } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/\?/).length).toBe(1)
})

it('renders a minutes percentage', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { unit: "minutes" } } }}>
            <MeasurementValue metric={{ type: "duration", scale: "percentage", unit: null, latest_measurement: { percentage: { value: "42" } } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/42%/).length).toBe(1)
})

it('renders an unknown minutes percentage', () => {
    render(
        <DataModel.Provider value={{ metrics: { duration: { unit: "minutes" } } }}>
            <MeasurementValue metric={{ type: "duration", scale: "percentage", unit: null, latest_measurement: { percentage: { value: null } } }} />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/\?%/).length).toBe(1)
})

it('shows when the metric was last measured', async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue metric={{ status: "target_met", type: "violations", scale: "count", unit: null, latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: "42" } } }} />
        </DataModel.Provider>
    )
    userEvent.hover(screen.queryByText(/42/))
    await waitFor(() => {
        expect(screen.queryByText(/Metric was last measured/)).not.toBe(null)
    })
})

it('shows when the last measurement attempt was', async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue metric={{ status: null, type: "violations", scale: "count", unit: null, latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: null } } }} />
        </DataModel.Provider>
    )
    userEvent.hover(screen.queryByText(/\?/))
    await waitFor(() => {
        expect(screen.queryByText(/Last measurement attempt/)).not.toBe(null)
    })
})
