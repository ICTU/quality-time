import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as fetch_server_api from '../api/fetch_server_api';
import { IssueTracker } from './IssueTracker';

jest.mock("../api/fetch_server_api.js")
fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });

function render_issue_tracker({ report = { report_uuid: "report_uuid", title: "Report" }, help_url = "" } = {}) {
    return render(
        <DataModel.Provider value={{ sources: { jira: { name: "Jira", issue_tracker: true, parameters: { private_token: { help_url: help_url } } } } }}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <IssueTracker
                    report={report}
                    reload={() => { /* Dummy implementation */ }}
                />
            </Permissions.Provider>
        </DataModel.Provider>
    )
}

it('sets the issue tracker type', async () => {
    await act(async () => {
        render_issue_tracker();
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker type/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Jira/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/type", { type: "jira" });
});

it('sets the issue tracker url', async () => {
    await act(async () => {
        render_issue_tracker();
    });
    await userEvent.type(screen.getByText(/URL/), 'https://jira{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/url", { url: "https://jira" });
});

it('sets the issue tracker username', async () => {
    await act(async () => {
        render_issue_tracker();
    });
    await userEvent.type(screen.getByText(/Username/), 'janedoe{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/username", { username: "janedoe" });
});

it('sets the issue tracker password', async () => {
    await act(async () => {
        render_issue_tracker();
    });
    await userEvent.type(screen.getByText(/Password/), 'secret{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/password", { password: "secret" });
});

it('sets the issue tracker private token', async () => {
    await act(async () => {
        render_issue_tracker();
    });
    await userEvent.type(screen.getByText(/Private token/), 'secret{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/private_token", { private_token: "secret" });
});

it('does not show the issue tracker private token help url', async () => {
    await act(async () => {
        const { container } = render_issue_tracker({ report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira" } });
        expect(container.querySelector("a")).toBe(null)
    });
});

it('shows the issue tracker private token help url', async () => {
    await act(async () => {
        const { container} = render_issue_tracker({ report: { report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira" } }, help_url: "https://help"});
        expect(container.querySelector("a")).toHaveAttribute('href', 'https://help')
    });
});
