import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import dayjs from "dayjs"
import history from "history/browser"
import { vi } from "vitest"

import * as auth from "./api/auth"
import * as datamodel from "./api/datamodel"
import * as fetchServerApi from "./api/fetch_server_api"
import * as report from "./api/report"
import App from "./App"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import {
    clickButton,
    clickRole,
    clickText,
    expectAltText,
    expectLabelText,
    expectNoAccessibilityViolations,
    expectNoAltText,
    expectNoLabelText,
    expectNoText,
    expectText,
    expectTextAfterWait,
} from "./testUtils"

function setUserInLocalStorage(hoursLeftInSession, email) {
    // sessionHoursLeft is the time in hours left in the current session. Can be negative for expired sessions.
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", email ?? "admin@example.org")
    const sessionExpirationDatetime = new Date(Date.now() + 60 * 60 * 1000 * hoursLeftInSession).toISOString()
    localStorage.setItem("session_expiration_datetime", sessionExpirationDatetime)
}

beforeAll(() => {
    global.EventSource = function () {
        return {
            addEventListener: vi.fn(),
            close: vi.fn(),
        }
    }
})

beforeEach(async () => {
    mockGetAnimations()
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockReturnValue({
        then: vi.fn().mockReturnValue({ catch: vi.fn().mockReturnValue({ finally: vi.fn() }) }),
    })
})

afterEach(() => vi.restoreAllMocks())

function reportDateButton() {
    return screen.getByLabelText(/Change report date/, { selector: "button" })
}

it("has no accessibility violations", async () => {
    const { container } = render(<App />)
    await expectNoAccessibilityViolations(container)
})

it("shows spinner", async () => {
    render(<App />)
    expectLabelText(/Loading/)
})

it("sets the user from local storage", async () => {
    setUserInLocalStorage(1)
    render(<App />)
    expectText(/admin/)
    expectAltText(/Avatar for admin/)
})

it("does not set invalid email addresses", async () => {
    setUserInLocalStorage(1, "admin at example.org")
    render(<App />)
    expectText(/admin/)
    expectNoAltText(/Avatar for admin/)
})

it("resets the user when the session is expired on mount", async () => {
    setUserInLocalStorage(-1)
    render(<App />)
    expectNoText(/admin/)
    expectText("Your session expired")
})

it("shows the expiry toast when the session expires while the app is running", async () => {
    vi.useFakeTimers()
    setUserInLocalStorage(1)
    render(<App />)
    expectText(/admin/)
    act(() => vi.advanceTimersByTime(60 * 60 * 1000 + 1))
    expectText("Your session expired")
    expectNoText(/admin/)
    vi.useRealTimers()
})

it("resets the user when the user clicks logout", async () => {
    setUserInLocalStorage(1)
    render(<App />)
    clickText(/admin/)
    clickText(/Logout/)
    expectNoText(/admin/)
})

it("logs in via forward authentication when the server returns ok", async () => {
    vi.spyOn(auth, "login").mockReturnValue(
        Promise.resolve({
            ok: true,
            email: "fwd@example.org",
            session_expiration_datetime: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
        }),
    )
    render(<App />)
    await expectTextAfterWait(/fwd@example.org/)
    expectAltText(/Avatar for fwd@example.org/)
    localStorage.clear()
})

it("shows an error toast when forward authentication rejects", async () => {
    vi.spyOn(auth, "login").mockReturnValue(Promise.reject(new Error("network down")))
    render(<App />)
    await expectTextAfterWait("Login with forward authentication failed")
    expectText(/network down/)
})

async function select15thOfPreviousMonth() {
    fireEvent.click(reportDateButton())
    clickButton("Previous month")
    clickRole("gridcell", "15", 0)
}

it("handles a date change", async () => {
    render(<App />)
    await select15thOfPreviousMonth()
    const expectedDate = dayjs().subtract(1, "month").date(15).toDate().toLocaleDateString()
    expect(reportDateButton().textContent).toMatch(expectedDate)
})

it("handles a date change between two dates in the past", async () => {
    history.push("/?report_date=2022-03-13")
    render(<App />)
    await select15thOfPreviousMonth()
    const expectedDate = dayjs("2022-03-13").subtract(1, "month").date(15).toDate().toLocaleDateString()
    expect(reportDateButton().textContent).toMatch(expectedDate)
})

it("reads the report date query parameter", async () => {
    history.push("/?report_date=2020-03-13")
    render(<App />)
    const expectedDate = dayjs("2020-03-13").toDate().toLocaleDateString()
    expect(reportDateButton().textContent).toMatch(expectedDate)
})

it("handles a date reset", async () => {
    history.push("/?report_date=2020-03-13")
    render(<App />)
    fireEvent.click(reportDateButton())
    clickButton("Today")
    expect(reportDateButton().textContent).toMatch(/today/)
})

it("navigates back to the reports overview when the home button is clicked", async () => {
    history.push("/some-uuid")
    render(<App />)
    const callsAfterMount = fetchServerApi.fetchServerApi.mock.calls.length
    clickRole("button", /Go to reports overview/)
    await waitFor(() => expect(history.location.pathname).toBe("/"))
    expect(fetchServerApi.fetchServerApi.mock.calls.length).toBeGreaterThan(callsAfterMount)
})

it("reloads on a browser pop but not on a push", async () => {
    render(<App />)
    const callsAfterMount = fetchServerApi.fetchServerApi.mock.calls.length
    history.push("/first-uuid")
    history.push("/second-uuid")
    const callsAfterPush = fetchServerApi.fetchServerApi.mock.calls.length
    history.back() // pops back to /first-uuid, which differs from the mount-time reportUuid ""
    await waitFor(() => expect(fetchServerApi.fetchServerApi.mock.calls.length).toBeGreaterThan(callsAfterPush))
    expect(callsAfterPush).toBe(callsAfterMount)
})

it("loads data and clears the loading spinner on a successful fetch", async () => {
    vi.spyOn(datamodel, "getDataModel").mockResolvedValue({ ok: true })
    vi.spyOn(report, "getReportsOverview").mockResolvedValue({})
    vi.spyOn(report, "getReport").mockResolvedValue({ ok: true, reports: [] })
    render(<App />)
    await waitFor(() => expectNoLabelText(/Loading/))
})

it("shows a server unreachable toast when a fetched response is not ok", async () => {
    vi.spyOn(datamodel, "getDataModel").mockResolvedValue({ ok: false })
    vi.spyOn(report, "getReportsOverview").mockResolvedValue({})
    vi.spyOn(report, "getReport").mockResolvedValue({ ok: true, reports: [] })
    render(<App />)
    await expectTextAfterWait("Server unreachable")
})

it("shows a server unreachable toast when a fetch rejects", async () => {
    vi.spyOn(datamodel, "getDataModel").mockRejectedValue(new Error("network down"))
    vi.spyOn(report, "getReportsOverview").mockResolvedValue({})
    vi.spyOn(report, "getReport").mockResolvedValue({ ok: true, reports: [] })
    render(<App />)
    await expectTextAfterWait("Server unreachable")
})

it("handles the nr of measurements event source", async () => {
    const eventListeners = {}
    global.EventSource = function () {
        return {
            addEventListener: function (event, listener) {
                eventListeners[event] = listener
            },
            close: vi.fn(),
        }
    }

    render(<App />)
    await act(async () => eventListeners["init"]({ data: 42 }))
    expectText("Not logged in")
    await act(async () => eventListeners["delta"]({ data: 42 }))
    await act(async () => eventListeners["delta"]({ data: 43 }))
    await act(async () => eventListeners["error"]())
    expectText("Server unreachable")
    await act(async () => eventListeners["init"]({ data: 43 }))
    expectText("Connected to server")
})

it("shows and hides a notification message", async () => {
    vi.useFakeTimers()
    render(<App />)
    await select15thOfPreviousMonth()
    expectText("Historic information is read-only")
    act(() => vi.advanceTimersByTime(50000))
    expectNoText("Historic information is read-only")
})
