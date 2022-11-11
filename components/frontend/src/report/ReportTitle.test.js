import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { ReportTitle } from './ReportTitle';
import * as changelog_api from '../api/changelog';
import * as report_api from '../api/report';

jest.mock("../api/changelog.js");
jest.mock("../api/report.js")

report_api.get_report_issue_tracker_options.mockImplementation(
    () => Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] })
)

changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));

const reload = () => { /* Dummy implementation */ }

function render_report_title() {
    render(
        <DataModel.Provider value={{ sources: { jira: { name: "Jira", issue_tracker: true } } }}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <ReportTitle
                    history={{ location: {} }}
                    report={{ report_uuid: "report_uuid", title: "Report" }}
                    reload={reload}
                />
            </Permissions.Provider>
        </DataModel.Provider>
    )
}

it('deletes the report', async () => {
    report_api.delete_report = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Delete report/)) });
    expect(report_api.delete_report).toHaveBeenLastCalledWith("report_uuid", undefined);
});

it('sets the title', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await userEvent.type(screen.getByLabelText(/Report title/), 'New title{Enter}', { initialSelectionStart: 0, initialSelectionEnd: 12 });
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "title", "New title", reload);
});

it('sets the subtitle', async () => {
    await act(async () => { render_report_title(); })
    fireEvent.click(screen.getByTitle(/expand/));
    await userEvent.type(screen.getByLabelText(/Report subtitle/), 'New subtitle{Enter}', { initialSelectionStart: 0, initialSelectionEnd: 12 });
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "subtitle", "New subtitle", reload);
});

it('sets the comment', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await userEvent.type(screen.getByLabelText(/Comment/), 'New comment{Shift>}{Enter}', { initialSelectionStart: 0, initialSelectionEnd: 8 });
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "comment", "New comment", reload);
});

it('sets the unknown status reaction time', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/reaction times/)) });
    await userEvent.type(screen.getByLabelText(/unknown status/), '4{Enter}}', { initialSelectionStart: 0, initialSelectionEnd: 1 });
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "desired_response_times", { "unknown": 4 }, reload);
})

it('sets the target not met status reaction time', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/reaction times/)) });
    await userEvent.type(screen.getByLabelText(/not meeting their target/), '5{Enter}}', { initialSelectionStart: 0, initialSelectionEnd: 1 });
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "desired_response_times", { "target_not_met": 5 }, reload);
})

it('sets the near target met status reaction time', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/reaction times/)) });
    await userEvent.type(screen.getByLabelText(/near their target/), '6{Enter}}', { initialSelectionStart: 0, initialSelectionEnd: 2 });
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "desired_response_times", { "near_target_met": 6 }, reload);
})

it('sets the issue tracker type', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker/)) });
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker type/)) });
    await act(async () => { fireEvent.click(screen.getByText(/Jira/)) });
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "type", "jira", reload);
});

it('sets the issue tracker url', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker/)) });
    await userEvent.type(screen.getByText(/URL/), 'https://jira{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "url", "https://jira", reload);
});

it('sets the issue tracker username', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker/)) });
    await userEvent.type(screen.getByText(/Username/), 'janedoe{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "username", "janedoe", reload);
});

it('sets the issue tracker password', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker/)) });
    await userEvent.type(screen.getByText(/Password/), 'secret{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "password", "secret", reload);
});

it('sets the issue tracker private token', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker/)) });
    await userEvent.type(screen.getByText(/Private token/), 'secret{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "private_token", "secret", reload);
});

it('loads the changelog', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    await act(async () => { fireEvent.click(screen.getByText(/Changelog/)) });
    expect(changelog_api.get_changelog).toHaveBeenCalledWith(5, { report_uuid: "report_uuid" });
});

it('shows the share tab', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    fireEvent.click(screen.getByText(/Share/));
    expect(screen.getAllByText(/Report permanent link/).length).toBe(1);
});

it('shows the notification destinations', async () => {
    await act(async () => { render_report_title(); });
    fireEvent.click(screen.getByTitle(/expand/));
    fireEvent.click(screen.getByText(/Notifications/));
    expect(screen.getAllByText(/No notification destinations/).length).toBe(2);
});
