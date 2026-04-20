import { render } from "@testing-library/react"
import { vi } from "vitest"

import { asyncClickText, expectNoText } from "../../testUtils"
import { SnackbarAlerts } from "../SnackbarAlerts"
import { PermLinkButton } from "./PermLinkButton"

function renderPermLinkButton({ showMessage = vi.fn() } = {}) {
    render(
        <SnackbarAlerts messages={[]} showMessage={showMessage}>
            <PermLinkButton itemType="metric" url="https://example.org" />
        </SnackbarAlerts>,
    )
}

test("PermLinkButton is not shown in an insecure context", () => {
    Object.assign(window, { isSecureContext: false })
    renderPermLinkButton()
    expectNoText(/Share/)
})

test("PermLinkButton copies URL to clipboard", async () => {
    const showMessage = vi.fn()
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: { writeText: vi.fn().mockImplementation(() => Promise.resolve()) },
    })
    renderPermLinkButton({ showMessage: showMessage })
    await asyncClickText(/Share/)
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://example.org")
    expect(showMessage).toHaveBeenCalledWith({ severity: "success", title: "Copied URL to clipboard" })
})

test("PermLinkButton shows error message if copying fails", async () => {
    const showMessage = vi.fn()
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: {
            writeText: vi.fn().mockImplementation(() => Promise.reject(new Error("fail"))),
        },
    })
    renderPermLinkButton({ showMessage: showMessage })
    await asyncClickText(/Share/)
    expect(showMessage).toHaveBeenCalledWith({
        severity: "error",
        title: "Could not copy URL to clipboard",
        description: "Error: fail",
    })
})
