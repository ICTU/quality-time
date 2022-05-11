import * as react_toastify from 'react-toastify';
import { show_message, show_connection_messages } from './toast';

jest.mock("react-toastify");

beforeEach(() => {
    jest.resetAllMocks()
});

it('shows a message', () => {
    show_message("error", "Error", "Description");
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(<><h4>Error</h4><p>Description</p></>);
});

it('shows a custom icon', () => {
    show_message("error", "Error", "Description", "question");
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(<><h4>Error</h4><p>Description</p></>);
});

it('shows no connection messages', () => {
    show_connection_messages({})
    expect(react_toastify.toast.mock.calls.length).toBe(0);
});

it('shows a successful connection message', () => {
    show_connection_messages({ availability: [{ status_code: 200 }] })
    expect(react_toastify.toast.mock.calls[0][0]).toEqual("URL connection OK");
});

it('shows a failed connection message', () => {
    show_connection_messages({ availability: [{ status_code: -1, reason: "Failure" }] })
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(<><h4>URL connection error</h4><p>Failure</p></>);
});

it('shows the http status code', () => {
    show_connection_messages({ availability: [{ status_code: 404, reason: "Not found" }] })
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(<><h4>URL connection error</h4><p>[HTTP status code 404] Not found</p></>);
});
