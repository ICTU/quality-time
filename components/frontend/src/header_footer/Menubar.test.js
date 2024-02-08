import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import history from 'history/browser';
import { Menubar } from './Menubar';
import * as auth from '../api/auth';
import { createTestableSettings } from '../__fixtures__/fixtures';

jest.mock("../api/auth.js")

beforeEach(() => {
    history.push("")
});

function renderMenubar(
    {
        openReportsOverview = null,
        panel = null,
        report_uuid = "report_uuid",
        set_user = null,
        user = null,
    } = {}
) {
    const settings = createTestableSettings()
    render(
        <Menubar
            onDate={() => {/* Dummy handler */ }}
            openReportsOverview={openReportsOverview}
            panel={panel}
            report_uuid={report_uuid}
            settings={settings}
            set_user={set_user}
            user={user}
        />
    );
}

it('logs in', async () => {
    auth.login = jest.fn().mockResolvedValue({ ok: true, email: "user@example.org", session_expiration_datetime: "2021-02-24T13:10:00+00:00" });
    const set_user = jest.fn();
    renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/));
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: 'user@example.org' } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: 'secret' } })
    await fireEvent.click(screen.getByText(/Submit/));
    expect(auth.login).toHaveBeenCalledWith("user@example.org", "secret")
    const expected_date = new Date(Date.parse("2021-02-24T13:10:00+00:00"));
    expect(set_user).toHaveBeenCalledWith("user@example.org", "user@example.org", expected_date)
});

it('shows invalid credential message', async () => {
    auth.login = jest.fn().mockResolvedValue({ ok: false });
    const set_user = jest.fn();
    renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/));
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: 'user@example.org' } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: 'secret' } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)));
    expect(screen.getAllByText(/Invalid credentials/).length).toBe(1);
    expect(auth.login).toHaveBeenCalledWith("user@example.org", "secret")
    expect(set_user).not.toHaveBeenCalled()
});

it('shows connection error message', async () => {
    auth.login = jest.fn().mockRejectedValue(new Error('Async error message'));
    const set_user = jest.fn();
    renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/));
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: 'user@example.org' } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: 'secret' } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)));
    expect(screen.getAllByText(/Connection error/).length).toBe(1);
    expect(auth.login).toHaveBeenCalledWith("user@example.org", "secret")
    expect(set_user).not.toHaveBeenCalled()
});

it('closes the dialog on escape', async () => {
    const set_user = jest.fn();
    renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/));
    await userEvent.type(screen.getByLabelText("Username"), "{Escape}");
    expect(screen.queryAllByText(/Username/).length).toBe(0);
})

it('logs out', async () => {
    auth.logout = jest.fn().mockResolvedValue({ ok: true });
    const set_user = jest.fn();
    renderMenubar({ set_user: set_user, user: "jadoe" })
    await fireEvent.click(screen.getByText(/Logout/));
    expect(auth.logout).toHaveBeenCalled()
    expect(set_user).toHaveBeenCalledWith(null)
});

it('does not go to home page if on reports overview', async () => {
    const openReportsOverview = jest.fn();
    renderMenubar({ report_uuid: "", openReportsOverview: openReportsOverview })
    act(() => { fireEvent.click(screen.getByAltText(/Go home/)) });
    expect(openReportsOverview).not.toHaveBeenCalled();
});

it('goes to home page if on report', async () => {
    const openReportsOverview = jest.fn();
    renderMenubar({ openReportsOverview: openReportsOverview })
    await act(async () => { fireEvent.click(screen.getByAltText(/Go home/)) })
    expect(openReportsOverview).toHaveBeenCalled();
});

it('goes to home page on keypress', async () => {
    const openReportsOverview = jest.fn();
    renderMenubar({ openReportsOverview: openReportsOverview })
    await userEvent.type(screen.getByAltText(/Go home/), "{Enter}");
    expect(openReportsOverview).toHaveBeenCalled();
});

it('shows the view panel on menu item click', () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
});

it('shows the view panel on space', async () => {
    renderMenubar({ report_uuid: "", panel: <div>Hello</div> })
    await userEvent.type(screen.getByText(/Settings/), " ")
    expect(screen.getAllByText(/Hello/).length).toBe(1)
})

it('hides the view panel on click', () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
});

it('hides the view panel on escape', async () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await userEvent.keyboard("{Escape}")
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
})
