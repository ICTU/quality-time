import React from 'react';
import { act, fireEvent, render, screen, waitForElementToBeRemoved } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Menubar } from './Menubar';
import * as auth from '../api/auth';

jest.mock("../api/auth.js")

it('logs in', async () => {
    auth.login = jest.fn().mockResolvedValue({ ok: true, email: "user@example.org", session_expiration_datetime: "2021-02-24T13:10:00+00:00" });
    const set_user = jest.fn();
    await act(async () => {
        render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} user={null} set_user={set_user} />);
        fireEvent.click(screen.getByText(/Login/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Submit/));
    });
    expect(auth.login).toHaveBeenCalled()
    const expected_date = new Date(Date.parse("2021-02-24T13:10:00+00:00"));
    expect(set_user).toHaveBeenCalledWith("", "user@example.org", expected_date)
});

it('logs out', async () => {
    auth.logout = jest.fn().mockResolvedValue({ ok: true });
    const set_user = jest.fn();
    await act(async () => {
        render(<Menubar user={"jadoe"} set_user={set_user} />);
        fireEvent.click(screen.getByText(/Logout/));
    });
    expect(auth.logout).toHaveBeenCalled()
    expect(set_user).toHaveBeenCalledWith(null)
});

it('does not go to home page if on reports overview', async () => {
    const go_home = jest.fn();
    await act(async () => {
        render(<Menubar go_home={go_home} />);
        fireEvent.click(screen.getByAltText(/Go home/));
    });
    expect(go_home).not.toHaveBeenCalled();
});

it('goes to home page if on report', async () => {
    const go_home = jest.fn();
    await act(async () => {
        render(<Menubar current_report={{}} go_home={go_home} />);
        fireEvent.click(screen.getByAltText(/Go home/));
    });
    expect(go_home).toHaveBeenCalled();
});

it('goes to home page on keypress', async () => {
    const go_home = jest.fn();
    await act(async () => {
        render(<Menubar go_home={go_home} />);
        userEvent.type(screen.getByAltText(/Go home/), "{Enter}");
    });
    expect(go_home).toHaveBeenCalled();
});

it('shows the view panel on menu item click', async () => {
    await act(async () => {
        render(<Menubar panel={<div>Hello</div>}/>);
        fireEvent.click(screen.getByText(/Settings/));
    });
    expect(screen.getAllByText(/Hello/).length).toBe(1)
})

it('shows the view panel on enter', async () => {
    await act(async () => {
        render(<Menubar panel={<div>Hello</div>} />);
        userEvent.type(screen.getByText(/Settings/), "{Enter}");
    });
    expect(screen.getAllByText(/Hello/).length).toBe(1)
})

it('hides the view panel on click', async () => {
    await act(async () => { render(<Menubar panel={<div>Hello</div>} />)})
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
})

it('hides the view panel on escape', async () => {
    await act(async () => { render(<Menubar panel={<div>Hello</div>} />)})
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await act(async() => {fireEvent.keyDown(screen.getByText(/Hello/), { key: 'Escape', code: 'Escape' })})
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
})

it('does not hide the view panel on another key', async () => {
    await act(async () => { render(<Menubar panel={<div>Hello</div>} />)})
    fireEvent.click(screen.getByText(/Settings/));
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await act(async() => {userEvent.keyboard("X")})
    expect(screen.queryAllByText(/Hello/).length).toBe(1)
})
