import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { ReadOnlyContext } from '../context/ReadOnly';
import { ReportTitle } from './ReportTitle';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

let mockHistory = { location: {} };

it('renders without crashing', () => {
    render(
        <ReportTitle
            history={mockHistory}
            report={{ title: "Report" }}
        />
    )
    expect(screen.getAllByText(/Report/).length).toBe(1);
});

it('deletes the report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {render(
        <ReadOnlyContext.Provider value={false}>
            <ReportTitle
                history={mockHistory}
                report={{ report_uuid: "report_uuid", title: "Report" }}
            />
        </ReadOnlyContext.Provider>
    )});
    await act(async () => {
        fireEvent.click(screen.getByTitle(/expand/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/report/report_uuid/5");
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete report/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("delete", "report/report_uuid", {});
});
