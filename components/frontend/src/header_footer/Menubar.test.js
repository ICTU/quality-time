import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { Menubar } from './Menubar';
import * as auth from '../api/auth';

jest.mock("../api/auth.js")

it('scrolls to the dashboard', async () => {
    const scrollIntoView = jest.fn();
    scrollIntoView.mockImplementation(() => { return { scrollIntoView: jest.fn() } });
    Object.defineProperty(global.document, 'getElementById', { value: scrollIntoView, configurable: true });
    Object.defineProperty(global.window, 'scrollBy', { value: jest.fn(), configurable: true });
    await act(async () => {
        render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} />);
        fireEvent.click(screen.getByLabelText(/Scroll to dashboard/));
    });
    expect(scrollIntoView).toHaveBeenCalled()
});

it('does not crash if there is no dashboard', async () => {
    Object.defineProperty(global.document, 'getElementById', { value: () => null, configurable: true });
    await act(async () => {
        render(<Menubar report_date_string="2019-10-10" onDate={() => {/* Dummy handler */ }} />);
        fireEvent.click(screen.getByLabelText(/Scroll to dashboard/));
    });
});

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
