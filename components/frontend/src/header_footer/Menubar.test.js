import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Menubar } from './Menubar';
import * as auth from '../api/auth';

jest.mock("../api/auth.js")

it('logs in', async () => {
    auth.login = jest.fn().mockResolvedValue({ ok: true, email: "user@example.org", session_expiration_datetime: "2021-02-24T13:10:00+00:00" });
    const set_user = jest.fn();
    render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} user={null} set_user={set_user} />);
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
    render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} user={null} set_user={set_user} />);
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
    render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} user={null} set_user={set_user} />);
    fireEvent.click(screen.getByText(/Login/));
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: 'user@example.org' } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: 'secret' } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)));
    expect(screen.getAllByText(/Connection error/).length).toBe(1);
    expect(auth.login).toHaveBeenCalledWith("user@example.org", "secret")
    expect(set_user).not.toHaveBeenCalled()
});

it('closes the dialog on escape', async() => {
    const set_user = jest.fn();
    render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} user={null} set_user={set_user} />);
    fireEvent.click(screen.getByText(/Login/));
    await userEvent.type(screen.getByLabelText("Username"), "{Escape}");
    expect(screen.queryAllByText(/Username/).length).toBe(0);
})

it('logs out', async () => {
    auth.logout = jest.fn().mockResolvedValue({ ok: true });
    const set_user = jest.fn();
    render(<Menubar user={"jadoe"} set_user={set_user} />);
    await fireEvent.click(screen.getByText(/Logout/));
    expect(auth.logout).toHaveBeenCalled()
    expect(set_user).toHaveBeenCalledWith(null)
});

it('does not go to home page if on reports overview', async () => {
    const openReportsOverview = jest.fn();
    render(<Menubar atReportsOverview={true} openReportsOverview={openReportsOverview} />);
    act(() => { fireEvent.click(screen.getByAltText(/Go home/)) });
    expect(openReportsOverview).not.toHaveBeenCalled();
});

it('goes to home page if on report', async () => {
    const openReportsOverview = jest.fn();
    render(<Menubar atReportsOverview={false} openReportsOverview={openReportsOverview} />);
    await act(async () => { fireEvent.click(screen.getByAltText(/Go home/)) })
    expect(openReportsOverview).toHaveBeenCalled();
});

it('goes to home page on keypress', async () => {
    const openReportsOverview = jest.fn();
    render(<Menubar openReportsOverview={openReportsOverview} />);
    await userEvent.type(screen.getByAltText(/Go home/), "{Enter}");
    expect(openReportsOverview).toHaveBeenCalled();
});

it('shows the view panel on menu item click', () => {
    render(<Menubar panel={<div>Hello</div>} />);
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
});

it('shows the view panel on space', async () => {
    render(<Menubar atReportsOverview={true} panel={<div>Hello</div>} />);
    await userEvent.type(screen.getByText(/Settings/), " ")
    expect(screen.getAllByText(/Hello/).length).toBe(1)
})

it('hides the view panel on click', () => {
    render(<Menubar panel={<div>Hello</div>} />)
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
});

it('hides the view panel on escape', async () => {
    render(<Menubar panel={<div>Hello</div>} />)
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await userEvent.keyboard("{Escape}")
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
})

it("clears the visible details tabs", () => {
    const clearVisibleDetailsTabs = jest.fn();
    render(<Menubar clearVisibleDetailsTabs={clearVisibleDetailsTabs} visibleDetailsTabs={["tab"]} />)
    fireEvent.click(screen.getByRole("button", { name: "Collapse all metrics" }))
    expect(clearVisibleDetailsTabs).toHaveBeenCalled()
})

it("doesn't clear the visible details tabs if there are none", () => {
    const clearVisibleDetailsTabs = jest.fn();
    render(<Menubar clearVisibleDetailsTabs={clearVisibleDetailsTabs} visibleDetailsTabs={[]} />)
    fireEvent.click(screen.getByRole("button", { name: "Collapse all metrics" }))
    expect(clearVisibleDetailsTabs).not.toHaveBeenCalled()
})
