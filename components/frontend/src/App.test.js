import { act, fireEvent, render, screen } from "@testing-library/react"
import dayjs from "dayjs"
import history from "history/browser"

import * as auth from "./api/auth"
import * as fetch_server_api from "./api/fetch_server_api"
import App from "./App"
import * as toast from "./widgets/toast"

function set_user_in_local_storage(session_expiration_datetime, email) {
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", email ?? "admin@example.org")
    localStorage.setItem("session_expiration_datetime", session_expiration_datetime)
}

beforeAll(() => {
    global.EventSource = jest.fn(() => ({
        addEventListener: jest.fn(),
        close: jest.fn(),
    }))
})

beforeEach(() => {
    history.push("")
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({
        then: jest.fn().mockReturnValue({ catch: jest.fn().mockReturnValue({ finally: jest.fn() }) }),
    })
})

afterEach(() => {
    jest.restoreAllMocks()
})

it("shows spinner", async () => {
    render(<App />)
    expect(screen.getAllByLabelText(/Loading/).length).toBe(1)
})

it("sets the user from local storage", () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z")
    render(<App />)
    expect(screen.getAllByText(/admin/).length).toBe(1)
    expect(screen.getAllByAltText(/Avatar/).length).toBe(1)
})

it("does not set invalid email addresses", () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z", "admin at example.org")
    render(<App />)
    expect(screen.getAllByText(/admin/).length).toBe(1)
    expect(screen.queryAllByAltText(/Avatar/).length).toBe(0)
})

it("resets the user when the session is expired on mount", () => {
    set_user_in_local_storage("2000-02-23T22:00:50.945Z")
    render(<App />)
    expect(screen.queryAllByText(/admin/).length).toBe(0)
})

it("resets the user when the user clicks logout", async () => {
    set_user_in_local_storage("3000-02-23T22:00:50.945Z")
    auth.logout = jest.fn().mockResolvedValue({ ok: true })
    render(<App />)
    await act(async () => {
        fireEvent.click(screen.getByText(/admin/))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Logout/))
    })
    expect(screen.queryAllByText(/admin/).length).toBe(0)
})

async function selectDate() {
    await act(async () => {
        fireEvent.click(screen.getByLabelText("Report date"))
    })
    await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Previous month" }))
    })
    await act(async () => {
        fireEvent.click(screen.getAllByRole("gridcell", { name: "15" })[0])
    })
}

it("handles a date change", async () => {
    render(<App />)
    await selectDate()
    const expectedDate = dayjs().subtract(1, "month").date(15).toDate().toDateString()
    expect(screen.getByLabelText("Report date").textContent).toMatch(expectedDate)
})

it("handles a date change between two dates in the past", async () => {
    history.push("/?report_date=2022-03-13")
    render(<App />)
    await selectDate()
    const expectedDate = dayjs().subtract(1, "month").date(15).toDate().toDateString()
    expect(screen.getByLabelText("Report date").textContent).toMatch(expectedDate)
})

it("reads the report date query parameter", () => {
    history.push("/?report_date=2020-03-13")
    render(<App />)
    const expectedDate = dayjs("2020-03-13").toDate().toDateString()
    expect(screen.getByLabelText("Report date").textContent).toMatch(expectedDate)
})

it("handles a date reset", async () => {
    history.push("/?report_date=2020-03-13")
    render(<App />)
    await act(async () => {
        fireEvent.click(screen.getByLabelText("Report date"))
    })
    await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: "Today" }))
    })
    expect(screen.getByLabelText("Report date").textContent).toMatch(/today/)
})

it("handles the nr of measurements event source", async () => {
    const eventSourceInstance = {
        addEventListener: jest.fn(),
        close: jest.fn(),
    }
    const eventListeners = {}

    eventSourceInstance.addEventListener.mockImplementation((event, listener) => {
        eventListeners[event] = listener
    })

    const showMessage = jest.spyOn(toast, "showMessage")
    global.EventSource = jest.fn(() => eventSourceInstance)

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
