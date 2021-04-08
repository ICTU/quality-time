import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EDIT_REPORT_PERMISSION, ReadOnlyContext } from '../context/ReadOnly';
import { NotificationDestinations } from './NotificationDestinations';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const notification_destinations= {
    destination_uuid1: {
        webhook: "",
        name: "new",
        url: ""
    }
};

function render_notification_destinations(destinations) {
  render(
    <ReadOnlyContext.Provider value={[EDIT_REPORT_PERMISSION]}>
      <NotificationDestinations destinations={destinations} report_uuid={"report_uuid"} reload={() => {}}/>
    </ReadOnlyContext.Provider>
  )
}

it('creates the first notification destination when the add notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render_notification_destinations({})
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Add notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/new`, {});
});

it('creates a new notification destination when the add notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render_notification_destinations(notification_destinations)
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Add notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/new`, {});
});

it('edits notification destination name attribute when it is changed in the input field', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render_notification_destinations(notification_destinations)
  });
  userEvent.type(screen.getByLabelText(/Name/), ' changed{enter}');

  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/destination_uuid1/attributes`, {name: "new changed"});
});

it('edits multiple notification destination attributes when they are changed in the input fields', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render_notification_destinations(notification_destinations)
  });
  userEvent.type(screen.getByPlaceholderText(/url/), 'new.webhook.com{enter}');

  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('post', `report/report_uuid/notification_destination/destination_uuid1/attributes`, {webhook: "new.webhook.com", url: "http://localhost/"});
});

it('removes the notification destination when the delete notification destination button is clicked', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render_notification_destinations(notification_destinations)
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Delete notification destination/));
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith('delete', `report/report_uuid/notification_destination/destination_uuid1`, {});
});
