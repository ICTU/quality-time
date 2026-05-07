import { vi } from "vitest"

import { showURLAvailabilityMessage } from "./messages"

const OK_200 = {
    description: "URL was accessed without errors",
    severity: "success",
    title: "URL connection OK",
}
const NOK_400 = {
    description: "[HTTP status code 400] Client error",
    severity: "warning",
    title: "URL connection error",
}
const UNKNOWN = {
    description: "Unknown error",
    severity: "warning",
    title: "URL connection error",
}

describe("showURLAvailabilityMessage", () => {
    it("shows no message when there is no URL availability status", () => {
        const showMessage = vi.fn()
        showURLAvailabilityMessage({}, showMessage)
        expect(showMessage).not.toHaveBeenCalled()
    })
    it("shows a 200 message", () => {
        const showMessage = vi.fn()
        showURLAvailabilityMessage({ status_code: 200 }, showMessage)
        expect(showMessage).toHaveBeenCalledWith(OK_200)
    })
    it("shows a 400 message", () => {
        const showMessage = vi.fn()
        showURLAvailabilityMessage({ status_code: 400, reason: "Client error" }, showMessage)
        expect(showMessage).toHaveBeenCalledWith(NOK_400)
    })
    it("shows an unknown message", () => {
        const showMessage = vi.fn()
        showURLAvailabilityMessage({ status_code: -1, reason: "Unknown error" }, showMessage)
        expect(showMessage).toHaveBeenCalledWith(UNKNOWN)
    })
})
