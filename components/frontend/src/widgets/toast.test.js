import { Icon } from 'semantic-ui-react';
import * as react_toastify from 'react-toastify';
import { show_message, show_connection_messages } from './toast';

jest.mock("react-toastify");

it('shows a message', () => {
    const toast_type = react_toastify.toast.TYPE;
    react_toastify.toast = jest.fn();
    react_toastify.toast.TYPE = toast_type;
    show_message("error", "Error", "Description");
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(<><h4><Icon name="close"/>Error</h4><p>Description</p></>);
});

it('shows a custom icon', () => {
    const toast_type = react_toastify.toast.TYPE;
    react_toastify.toast = jest.fn();
    react_toastify.toast.TYPE = toast_type;
    show_message("error", "Error", "Description", "question");
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(<><h4><Icon name="question"/>Error</h4><p>Description</p></>);
});

it('shows no connection messages', () => {
    const toast_type = react_toastify.toast.TYPE;
    react_toastify.toast = jest.fn();
    react_toastify.toast.TYPE = toast_type;
    show_connection_messages({})
    expect(react_toastify.toast.mock.calls.length).toBe(0);
});
  
it('shows a successful connection message', () => {
    const toast_type = react_toastify.toast.TYPE;
    react_toastify.toast = jest.fn();
    react_toastify.toast.TYPE = toast_type;
    show_connection_messages({availability: [{status_code: 200}]})
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(<><h4><Icon name="thumbs up"/>URL connection OK</h4><p/></>);
});
  
it('shows a failed connection message', () => {
    const toast_type = react_toastify.toast.TYPE;
    react_toastify.toast = jest.fn();
    react_toastify.toast.TYPE = toast_type;
    show_connection_messages({availability: [{status_code: -1, reason: "Failure"}]})
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(<><h4><Icon name="warning circle"/>URL connection error</h4><p>Failure</p></>);
});
  
it('shows the http status code', () => {
    const toast_type = react_toastify.toast.TYPE;
    react_toastify.toast = jest.fn();
    react_toastify.toast.TYPE = toast_type;
    show_connection_messages({availability: [{status_code: 404, reason: "Not found"}]})
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(<><h4><Icon name="warning circle"/>URL connection error</h4><p>[HTTP status code 404] Not found</p></>);
});
