import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { clickText, expectFetch, expectNoAccessibilityViolations } from "../testUtils"
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
    clickText(/Add notification destination/)
    expectFetch("post", "report/report_uuid/notification_destination/new", { report_url: "http://localhost:3000/" })
    await expectNoAccessibilityViolations(container)
})

it("creates a new notification destination when the add notification destination button is clicked", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    clickText(/Add notification destination/)
    expectFetch("post", "report/report_uuid/notification_destination/new", { report_url: "http://localhost:3000/" })
    await expectNoAccessibilityViolations(container)
})

it("edits notification destination name attribute when it is changed in the input field", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    await userEvent.type(screen.getByLabelText(/Webhook name/), " changed{Enter}")
    expectFetch("post", "report/report_uuid/notification_destination/destination_uuid1/attributes", {
        name: "new changed",
    })
    await expectNoAccessibilityViolations(container)
})

it("edits multiple notification destination attributes when they are changed in the input fields", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    await userEvent.type(screen.getByPlaceholderText(/https:\/\/example/), "new.webhook.com{Enter}")
    expectFetch("post", "report/report_uuid/notification_destination/destination_uuid1/attributes", {
        webhook: "new.webhook.com",
        url: "http://localhost:3000/",
    })
    await expectNoAccessibilityViolations(container)
})

it("removes the notification destination when the delete notification destination button is clicked", async () => {
    const { container } = renderNotificationDestinations(notificationDestinations)
    clickText(/Delete notification destination/)
    expectFetch("delete", "report/report_uuid/notification_destination/destination_uuid1", {})
    await expectNoAccessibilityViolations(container)
})
