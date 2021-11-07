import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
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

it('goes to home page', async () => {
    const go_home = jest.fn();
    await act(async () => {
        render(<Menubar go_home={go_home} />);
        fireEvent.click(screen.getByAltText(/Go home/));
    });
    expect(go_home).toHaveBeenCalled();
});
