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
    asyncClickText,
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

afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
})

function mockSuccessfulFetches({ reports = [] } = {}) {
    vi.spyOn(datamodel, "getDataModel").mockResolvedValue({ ok: true, subjects: {}, metrics: {}, sources: {} })
    vi.spyOn(report, "getReportsOverview").mockResolvedValue({})
    vi.spyOn(report, "getReport").mockResolvedValue({ ok: true, reports })
}

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
})

it("shows an error toast when forward authentication rejects", async () => {
    vi.spyOn(auth, "login").mockReturnValue(Promise.reject(new Error("network down")))
    render(<App />)
    await expectTextAfterWait("Login with forward authentication failed")
    expectText(/network down/)
})

it("does not log in via forward authentication when the server returns not ok", async () => {
    vi.spyOn(auth, "login").mockResolvedValue({ ok: false })
    render(<App />)
    expectText("Not logged in")
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

it("navigates to a report when its card is clicked", async () => {
    mockSuccessfulFetches({ reports: [{ report_uuid: "report_uuid", title: "Report title", subjects: {} }] })
    render(<App />)
    await expectTextAfterWait(/Report title/)
    await asyncClickText(/Report title/)
    await waitFor(() => expect(history.location.pathname).toBe("/report_uuid"))
})

it("navigates back to the reports overview when the home button is clicked", async () => {
    history.push("/some-uuid")
    render(<App />)
    const callsAfterMount = fetchServerApi.fetchServerApi.mock.calls.length
    clickRole("button", /Go to reports overview/)
    await waitFor(() => expect(history.location.pathname).toBe("/"))
    expect(fetchServerApi.fetchServerApi.mock.calls.length).toBeGreaterThan(callsAfterMount)
})

it("handles a non-200 availability in a reload response", async () => {
    setUserInLocalStorage(1)
    mockSuccessfulFetches()
    render(<App />)
    await expectTextAfterWait(/Add report/)
    fetchServerApi.fetchServerApi.mockResolvedValueOnce({
        ok: true,
        availability: { status_code: 503, reason: "Service Unavailable" },
    })
    await asyncClickText(/Add report/)
    await expectTextAfterWait(/URL connection error/)
})

it("does not warn about an expired session when forward auth recovers it", async () => {
    setUserInLocalStorage(1)
    mockSuccessfulFetches()
    vi.spyOn(auth, "login").mockResolvedValue({
        ok: true,
        email: "fwd@example.org",
        session_expiration_datetime: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
    })
    render(<App />)
    await expectTextAfterWait(/Add report/)
    fetchServerApi.fetchServerApi.mockResolvedValueOnce({ ok: false, status: 401 })
    await asyncClickText(/Add report/)
    await waitFor(() => expect(screen.queryAllByText(/fwd@example.org/).length).toBeGreaterThan(0))
    expectNoText(/Your session expired/)
})

it("warns about an expired session when a reload returns 401", async () => {
    setUserInLocalStorage(1)
    mockSuccessfulFetches()
    vi.spyOn(auth, "login").mockResolvedValue({ ok: false })
    render(<App />)
    await expectTextAfterWait(/Add report/)
    fetchServerApi.fetchServerApi.mockResolvedValueOnce({ ok: false, status: 401 })
    await asyncClickText(/Add report/)
    await expectTextAfterWait(/Your session expired/)
})

it("ignores stale report fetches when the user navigates mid-fetch", async () => {
    let resolveStale
    mockSuccessfulFetches({ reports: [{ report_uuid: "first", title: "Fresh report", subjects: {} }] })
    vi.spyOn(report, "getReport").mockImplementationOnce(() => new Promise((resolve) => (resolveStale = resolve)))
    render(<App />)
    history.push("/first")
    history.push("/second")
    history.back()
    await waitFor(() => expect(screen.queryAllByText(/Fresh report/).length).toBeGreaterThan(0))
    await act(async () =>
        resolveStale({
            ok: true,
            reports: [{ report_uuid: "stale", title: "Stale report", subjects: {} }],
        }),
    )
    expectNoText(/Stale report/)
    expectNoText(/Sorry, this report/)
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

it("handles a report response without a reports field", async () => {
    mockSuccessfulFetches()
    vi.spyOn(report, "getReport").mockResolvedValue({ ok: true })
    render(<App />)
    await waitFor(() => expectNoLabelText(/Loading/))
})

it("loads data and clears the loading spinner on a successful fetch", async () => {
    mockSuccessfulFetches()
    render(<App />)
    await waitFor(() => expectNoLabelText(/Loading/))
})

it("shows a server unreachable toast when a fetched response is not ok", async () => {
    mockSuccessfulFetches()
    vi.spyOn(datamodel, "getDataModel").mockResolvedValue({ ok: false })
    render(<App />)
    await expectTextAfterWait("Server unreachable")
})

it("shows a server unreachable toast when a fetch rejects", async () => {
    mockSuccessfulFetches()
    vi.spyOn(datamodel, "getDataModel").mockRejectedValue(new Error("network down"))
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

it("does not duplicate a notification message", async () => {
    render(<App />)
    await select15thOfPreviousMonth()
    expectText("Historic information is read-only")
    fireEvent.click(reportDateButton())
    clickButton("Today")
    await select15thOfPreviousMonth()
    expectText("Historic information is read-only", 1)
})

it("shows and hides a notification message", async () => {
    vi.useFakeTimers()
    render(<App />)
    await select15thOfPreviousMonth()
    expectText("Historic information is read-only")
    act(() => vi.advanceTimersByTime(50000))
    expectNoText("Historic information is read-only")
})
