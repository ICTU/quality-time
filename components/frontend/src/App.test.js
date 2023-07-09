import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event';
import history from 'history/browser';
import App from './App';
import * as fetch_server_api from './api/fetch_server_api';

function set_user_in_local_storage(session_expiration_datetime, email) {
    localStorage.setItem("user", "admin");
    localStorage.setItem("email", email ?? "admin@example.org");
    localStorage.setItem("session_expiration_datetime", session_expiration_datetime);
}

beforeAll(() => {
    global.EventSource = jest.fn(() => ({
        addEventListener: jest.fn(),
        close: jest.fn()
    }))
    Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation(_query => ({
            matches: false,
            addEventListener: () => { /* No implementation needed */ },
            removeEventListener: () => { /* No implementation needed */ },
        })),
    });
});

beforeEach(() => {
    history.push("")
})

it('shows spinner', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<App />);
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
});

it('sets the user from local storage', () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z");
    render(<App />);
    expect(screen.getAllByText(/admin/).length).toBe(1)
    expect(screen.getAllByAltText(/Avatar/).length).toBe(1)
});

it('does not set invalid email addresses', () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z", "admin at example.org");
    render(<App />);
    expect(screen.getAllByText(/admin/).length).toBe(1)
    expect(screen.queryAllByAltText(/Avatar/).length).toBe(0)
});

it('resets the user when the session is expired on mount', () => {
    set_user_in_local_storage("2000-02-23T22:00:50.945Z");
    render(<App />);
    expect(screen.queryAllByText(/admin/).length).toBe(0)
});

it('resets the user when the user clicks logout', async () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z");
    render(<App />);
    await act(async () => { fireEvent.click(screen.getByText(/admin/)) })
    await act(async () => { fireEvent.click(screen.getByText(/Logout/)) })
    expect(screen.queryAllByText(/admin/).length).toBe(0)
})

it('handles a date change', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<App />);
    await userEvent.type(screen.getByTestId("datepicker-input"), "2020-03-13")
    expect(screen.getAllByDisplayValue("2020-03-13").length).toBe(1)
});

it('reads the report date query parameter', () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    history.push("/?report_date=2020-03-13")
    render(<App />);
    expect(screen.getAllByDisplayValue("2020-03-13").length).toBe(1)
});

it('handles a date reset', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    history.push("/?report_date=2020-03-13")
    render(<App />);
    await act(async () => { fireEvent.click(screen.getByTestId("datepicker-clear-icon")) })
    expect(screen.queryAllByDisplayValue("2020-03-13").length).toBe(0)
});
