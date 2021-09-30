import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { ReportsTitle } from './ReportsTitle';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

function render_reports_title() {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsTitle permissions={{}} get_changelog={() => { /* Do nothing */ }} />
        </Permissions.Provider>
    )
}

it('sets the title', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report overview title/), '{selectall}{del}New title{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/title", { title: "New title" });
});

it('sets the subtitle', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report overview subtitle/), '{selectall}{del}New subtitle{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/subtitle", { subtitle: "New subtitle" });
});

it('sets the edit report permission', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Permissions/));
    });
    userEvent.type(screen.getAllByText(/All authenticated users/)[0], 'jadoe{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/permissions", { permissions: { edit_reports: ["jadoe"] } });
})

it('sets the edit entities permission', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Permissions/));
    });
    userEvent.type(screen.getAllByText(/All authenticated users/)[1], 'jodoe{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/permissions", { permissions: { edit_entities: ["jodoe"] } });
})

it('loads the changelog', async () => {
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Changelog/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/5");
});
