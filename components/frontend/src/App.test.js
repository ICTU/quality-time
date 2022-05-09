import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event';
import App from './App';
import * as fetch_server_api from './api/fetch_server_api';

jest.mock("./api/fetch_server_api.js")

function set_user_in_local_storage(session_expiration_datetime) {
    localStorage.setItem("user", "admin");
    localStorage.setItem("email", "admin@example.org");
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

it('goes home', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<App />);
    fireEvent.click(screen.getAllByText("Quality-time")[0])
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
});

it('sets the user from local storage', () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z");
    render(<App />);
    expect(screen.getAllByText(/admin/).length).toBe(1)
});

it('resets the user when the session is expired on mount', () => {
    set_user_in_local_storage("2000-02-23T22:00:50.945Z");
    render(<App />);
    expect(screen.queryAllByText(/admin/).length).toBe(0)
});

it('handles a date change', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<App />);
    await userEvent.type(screen.getByLabelText("Report date"), "13-03-2020")
    expect(screen.getAllByDisplayValue(/13-03-2020/).length).toBe(1)
});
