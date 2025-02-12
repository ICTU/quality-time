import { act, fireEvent, render, screen } from "@testing-library/react"
import dayjs from "dayjs"
import history from "history/browser"
import { vi } from "vitest"

import * as auth from "./api/auth"
import * as fetch_server_api from "./api/fetch_server_api"
import App from "./App"
import { expectNoAccessibilityViolations } from "./testUtils"
import * as toast from "./widgets/toast"

vi.mock("./api/fetch_server_api.js")
vi.mock("./api/auth.js")
vi.mock("./widgets/toast.jsx")

function set_user_in_local_storage(session_expiration_datetime, email) {
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", email ?? "admin@example.org")
    localStorage.setItem("session_expiration_datetime", session_expiration_datetime)
}

beforeAll(() => {
    global.EventSource = vi.fn(() => ({
        addEventListener: vi.fn(),
        close: vi.fn(),
    }))
})

beforeEach(async () => {
    history.push("")
    fetch_server_api.api_with_report_date = (await vi.importActual("./api/fetch_server_api.js")).api_with_report_date
    fetch_server_api.fetch_server_api = vi.fn().mockReturnValue({
        then: vi.fn().mockReturnValue({ catch: vi.fn().mockReturnValue({ finally: vi.fn() }) }),
    })
    auth.login = vi.fn().mockResolvedValue({
        ok: false,
    })
})

afterEach(() => {
    vi.restoreAllMocks()
})

it("shows spinner", async () => {
    const { container } = render(<App />)
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("sets the user from local storage", async () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z")
    const { container } = render(<App />)
    expect(screen.getAllByText(/admin/).length).toBe(1)
    expect(screen.getAllByAltText(/Avatar for admin/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not set invalid email addresses", async () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z", "admin at example.org")
    const { container } = render(<App />)
    expect(screen.getAllByText(/admin/).length).toBe(1)
    expect(screen.queryAllByAltText(/Avatar for admin/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("resets the user when the session is expired on mount", async () => {
    set_user_in_local_storage("2000-02-23T22:00:50.945Z")
    const { container } = render(<App />)
    expect(screen.queryAllByText(/admin/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("resets the user when the user clicks logout", async () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z")
    auth.logout = vi.fn().mockResolvedValue({ ok: true })
    const { container } = render(<App />)
    fireEvent.click(screen.getByText(/admin/))
    fireEvent.click(screen.getByText(/Logout/))
    expect(screen.queryAllByText(/admin/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

async function selectDate(container) {
    fireEvent.click(screen.getByLabelText("Report date"))
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByRole("button", { name: "Previous month" }))
    fireEvent.click(screen.getAllByRole("gridcell", { name: "15" })[0])
}

it("handles a date change", async () => {
    const { container } = render(<App />)
    await selectDate(container)
    const expectedDate = dayjs().subtract(1, "month").date(15).toDate().toDateString()
    expect(screen.getByLabelText("Report date").textContent).toMatch(expectedDate)
    await expectNoAccessibilityViolations(container)
})

it("handles a date change between two dates in the past", async () => {
    history.push("/?report_date=2022-03-13")
    const { container } = render(<App />)
    await selectDate(container)
    const expectedDate = dayjs().subtract(1, "month").date(15).toDate().toDateString()
    expect(screen.getByLabelText("Report date").textContent).toMatch(expectedDate)
    await expectNoAccessibilityViolations(container)
})

it("reads the report date query parameter", async () => {
    history.push("/?report_date=2020-03-13")
    const { container } = render(<App />)
    const expectedDate = dayjs("2020-03-13").toDate().toDateString()
    expect(screen.getByLabelText("Report date").textContent).toMatch(expectedDate)
    await expectNoAccessibilityViolations(container)
})

it("handles a date reset", async () => {
    history.push("/?report_date=2020-03-13")
    const { container } = render(<App />)
    fireEvent.click(screen.getByLabelText("Report date"))
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByRole("button", { name: "Today" }))
    expect(screen.getByLabelText("Report date").textContent).toMatch(/today/)
    await expectNoAccessibilityViolations(container)
})

it("handles the nr of measurements event source", async () => {
    const eventSourceInstance = {
        addEventListener: vi.fn(),
        close: vi.fn(),
    }
    const eventListeners = {}

    eventSourceInstance.addEventListener.mockImplementation((event, listener) => {
        eventListeners[event] = listener
    })

    const showMessage = vi.spyOn(toast, "showMessage")
    global.EventSource = vi.fn(() => eventSourceInstance)

    render(<App />)
    await act(async () => eventListeners["init"]({ data: 42 }))
    expect(showMessage).toHaveBeenCalledWith(
        "info",
        "Not logged in",
        "You are not logged in. Editing is not possible until you are.",
    )
    await act(async () => eventListeners["delta"]({ data: 42 }))
    await act(async () => eventListeners["delta"]({ data: 43 }))
    await act(async () => eventListeners["error"]())
    expect(showMessage).toHaveBeenCalledWith(
        "error",
        "Server unreachable",
        "Trying to reconnect to server...",
        "reconnecting",
    )
    await act(async () => eventListeners["init"]({ data: 43 }))
    expect(showMessage).toHaveBeenCalledWith("success", "Connected to server", "Successfully reconnected to server.")
})
