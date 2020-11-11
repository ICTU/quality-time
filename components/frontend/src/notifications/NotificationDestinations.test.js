import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { ReadOnlyContext } from '../context/ReadOnly';
import { NotificationDestinations } from './NotificationDestinations';
import * as fetch_server_api from '../api/fetch_server_api';
import userEvent from '@testing-library/user-event';

jest.mock("../api/fetch_server_api.js")

const notification_destinations= {
    destination_uuid1: {
        teams_webhook: "",
        name: "new",
        url: ""
    }
};

it('creates the first notification destination when the add notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <NotificationDestinations destinations={{}} report_uuid={"report_uuid"} reload={() => {}}/>
      </ReadOnlyContext.Provider>);
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Add notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/new`, {});
});

it('creates a new notification destination when the add notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <NotificationDestinations destinations={notification_destinations} report_uuid={"report_uuid"} reload={() => {}}/>
      </ReadOnlyContext.Provider>);
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Add notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/new`, {});
});

it('edits notification destination attributes when these are changed in the input fields', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <NotificationDestinations destinations={notification_destinations} report_uuid={"report_uuid"} reload={() => {}}/>
      </ReadOnlyContext.Provider>);
  });
  userEvent.type(screen.getByLabelText(/Name/), ' changed{enter}');

  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/destination_uuid1/attributes`, {name: "new changed"});
});

it('removes the notification destination when the delete notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <NotificationDestinations destinations={notification_destinations} report_uuid={"report_uuid"} reload={() => {}}/>
      </ReadOnlyContext.Provider>);
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Delete notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('delete', `report/report_uuid/notification_destination/destination_uuid1`, {});
});
