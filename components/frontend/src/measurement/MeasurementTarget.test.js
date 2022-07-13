import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

it('does not render the technical debt popup if technical debt is not accepted', async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", target: "100", debt_end_date: "2022-12-31" }} />
        </DataModel.Provider>
    )
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/accepted as technical debt/).length).toBe(0)
    })
})

it('renders the technical debt popup if technical debt is accepted',  async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", target: "100", accept_debt: true, debt_end_date: "2021-12-31" }} />
        </DataModel.Provider>
    )
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/accepted as technical debt/).length).toBe(1)
    })
})

it('renders the technical debt popup if technical debt is accepted with a future end date',  async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", target: "100", accept_debt: true, debt_end_date: "3000-01-01" }} />
        </DataModel.Provider>
    )
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/accepted as technical debt until/).length).toBe(1)
    })
})

it('renders the issue status if all issues are done', async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", target: "100", accept_debt: true, issue_status: [{status_category: "done"}]}} />
        </DataModel.Provider>
    )
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/all issues for this metric have been marked done/).length).toBe(1)
    })
})

it('does not render the issue status if technical debt is not accepted', async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", target: "100", issue_status: [{status_category: "done"}]}} />
        </DataModel.Provider>
    )
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/all issues for this metric have been marked done/).length).toBe(0)
    })
})

it('renders both the issue status and the technical debt end date', async () => {
    render(
        <DataModel.Provider value={{ metrics: { violations: { direction: "<", unit: "violations" } } }}>
            <MeasurementTarget metric={{ type: "violations", target: "100", accept_debt: true, debt_end_date: "2021-12-31", issue_status: [{status_category: "done"}]}} />
        </DataModel.Provider>
    )
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/all issues for this metric have been marked done and technical debt was accepted/).length).toBe(1)
    })
})
