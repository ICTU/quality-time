import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReadOnlyContext } from '../context/ReadOnly';
import { ReportTitle } from './ReportTitle';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

function render_report_title() {
    render(
        <ReadOnlyContext.Provider value={false}>
            <ReportTitle
                history={{location: {}}}
                report={{ report_uuid: "report_uuid", title: "Report" }}
            />
        </ReadOnlyContext.Provider>
    ) 
}

it('deletes the report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/report/report_uuid/5");
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete report/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("delete", "report/report_uuid", {});
});

it('sets the title', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report title/), '{selectall}{del}New title{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/attribute/title", {title: "New title"});
});

it('sets the subtitle', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report subtitle/), '{selectall}{del}New subtitle{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/attribute/subtitle", {subtitle: "New subtitle"});
});
