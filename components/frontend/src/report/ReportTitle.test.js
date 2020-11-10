import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import ReactDOM from 'react-dom';
import { ReadOnlyContext } from '../context/ReadOnly';
import { ReportTitle } from './ReportTitle';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const report = {
    report_uuid: "report_uuid",
    title: "report title"
};

const reportWithDestination = {
    report_uuid: "report_uuid",
    title: "report title",
    notification_destinations: {
        destination_uuid1: {
            teams_webhook: "",
            name: "new",
            url: ""
        }
    }
};

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<ReportTitle
        report={{ title: "Report" }}
    />, div);
    ReactDOM.unmountComponentAtNode(div);
});

it('creates a new notification destination when the add notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <ReportTitle report={report} history={{location: {search: ""}}}/>
      </ReadOnlyContext.Provider>);
    fireEvent.click(screen.getByText(/report title/));
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Add notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/new`, {});
});

it('removes the notification destination when the delete notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <ReportTitle report={reportWithDestination} history={{location: {search: ""}}}/>
      </ReadOnlyContext.Provider>);
    fireEvent.click(screen.getByText(/report title/));
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Delete notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('delete', `report/report_uuid/notification_destination/destination_uuid1`, {});
});

it('edits notification destination attributes when these are changed in the input fields', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <ReportTitle report={report} history={{location: {search: ""}}}/>
      </ReadOnlyContext.Provider>);
    fireEvent.click(screen.getByText(/report title/));
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Add notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/destination_uuid1/attributes`, attributes);
});