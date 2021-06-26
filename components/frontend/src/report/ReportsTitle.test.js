import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { ReportsTitle } from './ReportsTitle';
import * as fetch_server_api from '../api/fetch_server_api';
import * as changelog_api from '../api/changelog';

jest.mock("../api/fetch_server_api.js")
jest.mock("../api/changelog.js");

function render_reports_title() {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsTitle permissions={[]} get_changelog={() => { /* Do nothing */ }} />
        </Permissions.Provider>
    ) 
}

it('sets the title', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report overview title/), '{selectall}{del}New title{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports/attribute/title", {title: "New title"});
});

it('sets the subtitle', async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report overview subtitle/), '{selectall}{del}New subtitle{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports/attribute/subtitle", {subtitle: "New subtitle"});
});
