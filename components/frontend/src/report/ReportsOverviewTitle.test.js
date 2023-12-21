import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import history from 'history/browser';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { ReportsOverviewTitle } from './ReportsOverviewTitle';
import * as fetch_server_api from '../api/fetch_server_api';
import { createTestableSettings } from '../__fixtures__/fixtures';

jest.mock("../api/fetch_server_api.js")

beforeEach(() => {
    history.push("?expanded=reports_overview:0")
})

function renderReportsOverviewTitle() {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverviewTitle reports_overview={{}} settings={createTestableSettings()} />
        </Permissions.Provider>
    )
}

it('sets the title', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderReportsOverviewTitle();
    await userEvent.type(screen.getByLabelText(/Report overview title/), '{Delete}New title{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/title", { title: "New title" });
});

it('sets the subtitle', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderReportsOverviewTitle();
    await userEvent.type(screen.getByLabelText(/Report overview subtitle/), '{Delete}New subtitle{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/subtitle", { subtitle: "New subtitle" });
});

it('sets the comment', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderReportsOverviewTitle();
    await userEvent.type(screen.getByLabelText(/Comment/), '{Delete}New comment{Shift>}{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/comment", { comment: "New comment" });
});

it('sets the edit report permission', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderReportsOverviewTitle();
    fireEvent.click(screen.getByText(/Permissions/));
    await userEvent.type(screen.getAllByText(/All authenticated users/)[0], 'jadoe{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/permissions", { permissions: { edit_reports: ["jadoe"] } });
})

it('sets the edit entities permission', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderReportsOverviewTitle();
    fireEvent.click(screen.getByText(/Permissions/));
    await userEvent.type(screen.getAllByText(/All authenticated users/)[1], 'jodoe{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/permissions", { permissions: { edit_entities: ["jodoe"] } });
})

it('loads the changelog', async () => {
    renderReportsOverviewTitle();
    await act(async () => { fireEvent.click(screen.getByText(/Changelog/)); });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/5");
});
