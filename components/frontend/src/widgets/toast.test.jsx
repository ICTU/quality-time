import history from "history/browser"
import * as reactToastify from "react-toastify"
import { vi } from "vitest"

import { showConnectionMessage, showMessage } from "./toast"

vi.mock("react-toastify")

beforeEach(() => history.push(""))

afterEach(() => vi.resetAllMocks())

it("shows a message", () => {
    showMessage("error", "Error", "Description")
    expect(reactToastify.toast.mock.calls[0][0]).toStrictEqual(
        <div>
            <b>Error</b>
            <p>Description</p>
        </div>,
    )
})

it("does not show a message when showing toasts has been turned off", () => {
    history.push("?hide_toasts=true")
    showMessage("error", "Error", "Description")
    expect(reactToastify.toast.mock.calls.length).toBe(0)
})

it("shows a custom icon", () => {
    showMessage("error", "Error", "Description", "question")
    expect(reactToastify.toast.mock.calls[0][0]).toStrictEqual(
        <div>
            <b>Error</b>
            <p>Description</p>
        </div>,
    )
})

it("shows no connection messages", () => {
    showConnectionMessage({})
    expect(reactToastify.toast.mock.calls.length).toBe(0)
})

it("shows a successful connection message", () => {
    showConnectionMessage({ availability: [{ status_code: 200 }] })
    expect(reactToastify.toast.mock.calls[0][0]).toEqual("URL connection OK")
})

it("shows a failed connection message", () => {
    showConnectionMessage({ availability: [{ status_code: -1, reason: "Failure" }] })
    expect(reactToastify.toast.mock.calls[0][0]).toEqual(
        <div>
            <b>URL connection error</b>
            <p>Failure</p>
        </div>,
    )
})

it("shows the http status code", () => {
    showConnectionMessage({ availability: [{ status_code: 404, reason: "Not found" }] })
    expect(reactToastify.toast.mock.calls[0][0]).toEqual(
        <div>
            <b>URL connection error</b>
            <p>[HTTP status code 404] Not found</p>
        </div>,
    )
})
