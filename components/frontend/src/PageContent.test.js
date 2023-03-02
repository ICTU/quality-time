import React from 'react';
import { act, render, screen } from '@testing-library/react';
import { PageContent } from './PageContent';
import * as fetch_server_api from './api/fetch_server_api';

jest.mock('./api/fetch_server_api', () => {
    const originalModule = jest.requireActual('./api/fetch_server_api');

    return {
        __esModule: true,
        ...originalModule,
        fetch_server_api: jest.fn().mockResolvedValue({ ok: true, measurements: [] }),
    };
});

beforeEach(() => {
    jest.clearAllMocks();
});

it('shows the reports overview', async () =>{
    await act(async () => render(<PageContent reports={[]} />))
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('shows that the report is missing', async () => {
    await act(async () => render(<PageContent history={{location: {}}} reports={[{}]} report_uuid="uuid" />))
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
})

it('shows that the report was missing', async () => {
    await act(async () => render(<PageContent dateOrder="ascending" history={{location: {}}} report_date={new Date("2022-03-31")} reports={[{}]} report_uuid="uuid" />))
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
})

it('shows the loading spinner', async () =>{
    await act(async () => render(<PageContent loading />))
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
})

it('fetches measurements if nr dates > 1', async () => {
    await act(async () => render(<PageContent reports={[]} nrDates={2} />))
    const expectedDate = new Date()
    expectedDate.setDate(expectedDate.getDate() - 1);
    const expectedDateStr = expectedDate.toISOString().split("T")[0] + "T00:00:00.000Z"
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", `measurements?min_report_date=${expectedDateStr}`);
})

it('fetches measurements if nr dates > 1 and time traveling', async () => {
    await act(async () => render(<PageContent reports={[]} nrDates={2} report_date={new Date(Date.UTC(2022, 3, 26))} />))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "measurements?report_date=2022-04-26T00:00:00.000Z&min_report_date=2022-04-25T00:00:00.000Z");
})

it('fetches measurements if nr dates == 1', async () => {
    await act(async () => render(<PageContent reports={[]} nrDates={1} />))
    const expectedDate = new Date()
    const expectedDateStr = expectedDate.toISOString().split("T")[0] + "T00:00:00.000Z"
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", `measurements?min_report_date=${expectedDateStr}`);
})
