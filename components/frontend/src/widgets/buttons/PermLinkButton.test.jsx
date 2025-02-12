import { act, fireEvent, render, screen } from "@testing-library/react"
import { vi } from "vitest"

import * as toast from "../toast"
import { PermLinkButton } from "./PermLinkButton"

vi.mock("../toast.jsx")

test("PermLinkButton is not shown in an insecure context", () => {
    Object.assign(window, { isSecureContext: false })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    expect(screen.queryAllByText(/Share/).length).toBe(0)
})

test("PermLinkButton copies URL to clipboard", async () => {
    toast.showMessage = vi.fn()
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: { writeText: vi.fn().mockImplementation(() => Promise.resolve()) },
    })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    await act(async () => {
        fireEvent.click(screen.getByText(/Share/))
    })
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://example.org")
    expect(toast.showMessage).toHaveBeenCalledWith("success", "Copied URL to clipboard")
})

test("PermLinkButton shows error message if copying fails", async () => {
    toast.showMessage = vi.fn()
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: {
            writeText: vi.fn().mockImplementation(() => Promise.reject(new Error("fail"))),
        },
    })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    await act(async () => {
        fireEvent.click(screen.getByText(/Share/))
    })
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not copy URL to clipboard", "Error: fail")
})
