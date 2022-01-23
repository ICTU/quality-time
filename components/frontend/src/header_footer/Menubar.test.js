import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
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
    const setPanelVisible = jest.fn()
    await act(async () => {
        render(<Menubar setPanelVisible={setPanelVisible} />);
        fireEvent.click(screen.getByText(/Settings/));
    });
    expect(setPanelVisible).toHaveBeenCalledWith(true)
})

it('shows the view panel on enter', async () => {
    const setPanelVisible = jest.fn()
    await act(async () => {
        render(<Menubar setPanelVisible={setPanelVisible} />);
        userEvent.type(screen.getByText(/Settings/), "{Enter}");
    });
    expect(setPanelVisible).toHaveBeenCalledWith(true)
})

it('hides the view panel on click', async () => {
    const setPanelVisible = jest.fn()
    await act(async () => { render(<Menubar panelVisible={true} setPanelVisible={setPanelVisible}/>) });
    fireEvent.click(screen.getByText(/Settings/));
    expect(setPanelVisible).toHaveBeenCalledWith(false)
})
