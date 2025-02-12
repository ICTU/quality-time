import history from "history/browser"
import * as react_toastify from "react-toastify"
import { vi } from "vitest"

import { showConnectionMessage, showMessage } from "./toast"

vi.mock("react-toastify")

beforeEach(() => {
    vi.resetAllMocks()
    history.push("")
})

it("shows a message", () => {
    showMessage("error", "Error", "Description")
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(
        <div>
            <b>Error</b>
            <p>Description</p>
        </div>,
    )
})

it("does not show a message when showing toasts has been turned off", () => {
    history.push("?hide_toasts=true")
    showMessage("error", "Error", "Description")
    expect(react_toastify.toast.mock.calls.length).toBe(0)
})

it("shows a custom icon", () => {
    showMessage("error", "Error", "Description", "question")
    expect(react_toastify.toast.mock.calls[0][0]).toStrictEqual(
        <div>
            <b>Error</b>
            <p>Description</p>
        </div>,
    )
})

it("shows no connection messages", () => {
    showConnectionMessage({})
    expect(react_toastify.toast.mock.calls.length).toBe(0)
})

it("shows a successful connection message", () => {
    showConnectionMessage({ availability: [{ status_code: 200 }] })
    expect(react_toastify.toast.mock.calls[0][0]).toEqual("URL connection OK")
})

it("shows a failed connection message", () => {
    showConnectionMessage({ availability: [{ status_code: -1, reason: "Failure" }] })
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(
        <div>
            <b>URL connection error</b>
            <p>Failure</p>
        </div>,
    )
})

it("shows the http status code", () => {
    showConnectionMessage({ availability: [{ status_code: 404, reason: "Not found" }] })
    expect(react_toastify.toast.mock.calls[0][0]).toEqual(
        <div>
            <b>URL connection error</b>
            <p>[HTTP status code 404] Not found</p>
        </div>,
    )
})
