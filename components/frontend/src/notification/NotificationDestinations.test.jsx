import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { NotificationDestinations } from "./NotificationDestinations"

const notificationDestinations = {
    destination_uuid1: {
        webhook: "",
        name: "new",
    },
}

function renderNotificationDestinations(destinations) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <NotificationDestinations
                destinations={destinations}
                reportUuid={"report_uuid"}
                reload={() => {
                    /* No need to reload during tests */
                }}
            />
        </Permissions.Provider>,
    )
}

beforeAll(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

it("creates the first notification destination when the add notification destination button is clicked", async () => {
    const { container } = renderNotificationDestinations({})
    fireEvent.click(screen.getByText(/Add notification destination/))
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith(
        "post",
        "report/report_uuid/notification_destination/new",
        { report_url: "http://localhost:3000/" },
    )
    await expectNoAccessibilityViolations(container)
})

it("creates a new notification destination when the add notification destination button is clicked", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    fireEvent.click(screen.getByText(/Add notification destination/))
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith(
        "post",
        "report/report_uuid/notification_destination/new",
        { report_url: "http://localhost:3000/" },
    )
    await expectNoAccessibilityViolations(container)
})

it("edits notification destination name attribute when it is changed in the input field", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    await userEvent.type(screen.getByLabelText(/Webhook name/), " changed{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith(
        "post",
        "report/report_uuid/notification_destination/destination_uuid1/attributes",
        { name: "new changed" },
    )
    await expectNoAccessibilityViolations(container)
})

it("edits multiple notification destination attributes when they are changed in the input fields", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    await userEvent.type(screen.getByPlaceholderText(/https:\/\/example/), "new.webhook.com{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith(
        "post",
        "report/report_uuid/notification_destination/destination_uuid1/attributes",
        { webhook: "new.webhook.com", url: "http://localhost:3000/" },
    )
    await expectNoAccessibilityViolations(container)
})

it("removes the notification destination when the delete notification destination button is clicked", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    fireEvent.click(screen.getByText(/Delete notification destination/))
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith(
        "delete",
        "report/report_uuid/notification_destination/destination_uuid1",
        {},
    )
    await expectNoAccessibilityViolations(container)
})
