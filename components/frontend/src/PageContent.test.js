import React from 'react';
import { act, render, screen } from '@testing-library/react';
import history from 'history/browser';
import { PageContent } from './PageContent';
import * as fetch_server_api from './api/fetch_server_api';
import { mockGetAnimations } from './dashboard/MockAnimations';
import { createTestableSettings } from './__fixtures__/fixtures';

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
    mockGetAnimations()
    history.push("")
});

async function renderPageContent(
    {
        loading = false,
        reports = [],
        report_date = null,
        report_uuid = ""
    } = {}
) {
    const settings = createTestableSettings()
    await act(
        async () => render(
            <div id="dashboard">
                <PageContent
                    loading={loading}
                    reports={reports}
                    reports_overview={{}}
                    report_date={report_date}
                    report_uuid={report_uuid}
                    settings={settings}
                />
            </div>
        )
    )
}

it('shows the reports overview', async () => {
    await renderPageContent({ report_date: new Date(2023, 10, 25) })
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('shows that the report is missing', async () => {
    await renderPageContent({ reports: [{}], report_uuid: "uuid" })
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
})

it('shows that the report was missing', async () => {
    await renderPageContent({ report_date: new Date("2022-03-31"), reports: [{}], report_uuid: "uuid" })
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
})

it('shows the loading spinner', async () => {
    await renderPageContent({ loading: true })
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
})

it('fetches measurements if nr dates > 1', async () => {
    history.push("?date_interval=1&nr_dates=2")
    await renderPageContent()
    const expectedDate = new Date()
    expectedDate.setDate(expectedDate.getDate() - 1);
    const expectedDateStr = expectedDate.toISOString().split("T")[0] + "T00:00:00.000Z"
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", `measurements?min_report_date=${expectedDateStr}`);
})

it('fetches measurements if nr dates > 1 and time traveling', async () => {
    history.push("?date_interval=1&nr_dates=2")
    await renderPageContent({ report_date: new Date(Date.UTC(2022, 3, 26)) })
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "measurements?report_date=2022-04-26T00:00:00.000Z&min_report_date=2022-04-25T00:00:00.000Z");
})

it('fetches measurements if nr dates == 1', async () => {
    history.push("?nr_dates=1")
    await renderPageContent()
    const expectedDate = new Date()
    const expectedDateStr = expectedDate.toISOString().split("T")[0] + "T00:00:00.000Z"
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", `measurements?min_report_date=${expectedDateStr}`);
})
