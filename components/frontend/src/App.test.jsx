import { act, fireEvent, render, screen } from "@testing-library/react"
import dayjs from "dayjs"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "./api/fetch_server_api"
import App from "./App"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import {
    clickButton,
    clickRole,
    clickText,
    expectLabelText,
    expectNoAccessibilityViolations,
    expectNoLabelText,
    expectNoText,
    expectText,
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
    expect(screen.getAllByAltText(/Avatar for admin/).length).toBe(1)
})

it("does not set invalid email addresses", async () => {
    setUserInLocalStorage(1, "admin at example.org")
    render(<App />)
    expectText(/admin/)
    expectNoLabelText(/Avatar for admin/)
})

it("resets the user when the session is expired on mount", async () => {
    setUserInLocalStorage(-1)
    render(<App />)
    expectNoText(/admin/)
    expectText("Your session expired")
})

it("resets the user when the user clicks logout", async () => {
    setUserInLocalStorage(1)
    render(<App />)
    clickText(/admin/)
    clickText(/Logout/)
    expectNoText(/admin/)
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
