import { render } from "@testing-library/react"
import { vi } from "vitest"

import { asyncClickText, expectNoText } from "../../testUtils"
import * as toast from "../toast"
import { PermLinkButton } from "./PermLinkButton"

beforeEach(() => {
    vi.spyOn(toast, "showMessage")
})

test("PermLinkButton is not shown in an insecure context", () => {
    Object.assign(window, { isSecureContext: false })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    expectNoText(/Share/)
})

test("PermLinkButton copies URL to clipboard", async () => {
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: { writeText: vi.fn().mockImplementation(() => Promise.resolve()) },
    })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    await asyncClickText(/Share/)
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://example.org")
    expect(toast.showMessage).toHaveBeenCalledWith("success", "Copied URL to clipboard")
})

test("PermLinkButton shows error message if copying fails", async () => {
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: {
            writeText: vi.fn().mockImplementation(() => Promise.reject(new Error("fail"))),
        },
    })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    await asyncClickText(/Share/)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not copy URL to clipboard", "Error: fail")
})
