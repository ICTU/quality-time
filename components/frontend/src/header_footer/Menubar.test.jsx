import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { expectNoAccessibilityViolations } from "../testUtils"
import { Menubar } from "./Menubar"

vi.mock("../api/fetch_server_api.js")

beforeEach(() => history.push(""))

afterEach(() => vi.resetAllMocks())

function renderMenubar({
    openReportsOverview = null,
    panel = null,
    report_uuid = "report_uuid",
    set_user = null,
    user = null,
} = {}) {
    const settings = createTestableSettings()
    return render(
        <Menubar
            onDate={() => {
                /* Dummy handler */
            }}
            openReportsOverview={openReportsOverview}
            panel={panel}
            report_uuid={report_uuid}
            settings={settings}
            set_user={set_user}
            user={user}
        />,
    )
}

it("logs in", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({
        ok: true,
        email: "user@example.org",
        session_expiration_datetime: "2021-02-24T13:10:00+00:00",
    })
    const set_user = vi.fn()
    const { container } = renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/))
    await expectNoAccessibilityViolations(container)
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "user@example.org" } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret" } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "login", {
        username: "user@example.org",
        password: "secret",
    })
    const expected_date = new Date(Date.parse("2021-02-24T13:10:00+00:00"))
    expect(set_user).toHaveBeenCalledWith("user@example.org", "user@example.org", expected_date)
    await expectNoAccessibilityViolations(container)
})

it("shows invalid credential message", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: false })
    const set_user = vi.fn()
    const { container } = renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/))
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "user@example.org" } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret" } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)))
    expect(screen.getAllByText(/Invalid credentials/).length).toBe(1)
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "login", {
        username: "user@example.org",
        password: "secret",
    })
    expect(set_user).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("shows connection error message", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockRejectedValue(new Error("Async error message"))
    const set_user = vi.fn()
    const { container } = renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/))
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: "user@example.org" } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret" } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)))
    expect(screen.getAllByText(/Connection error/).length).toBe(1)
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "login", {
        username: "user@example.org",
        password: "secret",
    })
    expect(set_user).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("closes the dialog on cancel", async () => {
    const set_user = vi.fn()
    const { container } = renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/))
    await act(async () => fireEvent.click(screen.getByText(/Cancel/)))
    await waitFor(async () => {
        expect(screen.queryAllByLabelText("Username").length).toBe(0)
        await expectNoAccessibilityViolations(container)
    })
    expect(set_user).not.toHaveBeenCalled()
})

it("closes the dialog on escape", async () => {
    const set_user = vi.fn()
    renderMenubar({ set_user: set_user })
    fireEvent.click(screen.getByText(/Login/))
    await userEvent.keyboard("{Escape}")
    await waitFor(() => {
        expect(screen.queryAllByLabelText("Username").length).toBe(0)
    })
    expect(set_user).not.toHaveBeenCalled()
})

it("logs out", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const set_user = vi.fn()
    const { container } = renderMenubar({ set_user: set_user, user: "jadoe" })
    fireEvent.click(screen.getByRole("button", { name: "User options" }))
    fireEvent.click(screen.getByRole("menuitem", { name: "Logout" }))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "logout", {})
    expect(set_user).toHaveBeenCalledWith(null)
    await expectNoAccessibilityViolations(container)
})

it("does not go to home page if on reports overview", async () => {
    const openReportsOverview = vi.fn()
    const { container } = renderMenubar({ report_uuid: "", openReportsOverview: openReportsOverview })
    act(() => {
        fireEvent.click(screen.getByAltText(/Go to reports overview/))
    })
    expect(openReportsOverview).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("goes to home page if on report", async () => {
    const openReportsOverview = vi.fn()
    const { container } = renderMenubar({ openReportsOverview: openReportsOverview })
    await act(async () => {
        fireEvent.click(screen.getByAltText(/Go to reports overview/))
    })
    expect(openReportsOverview).toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("goes to home page on keypress", async () => {
    const openReportsOverview = vi.fn()
    renderMenubar({ openReportsOverview: openReportsOverview })
    await userEvent.type(screen.getByAltText(/Go to reports overview/), "{Enter}")
    expect(openReportsOverview).toHaveBeenCalled()
})

it("shows the view panel on menu item click", async () => {
    const { container } = renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the view panel on space", async () => {
    renderMenubar({ report_uuid: "", panel: <div>Hello</div> })
    await userEvent.type(screen.getByText(/Settings/), " ")
    expect(screen.getAllByText(/Hello/).length).toBe(1)
})

it("hides the view panel on click", async () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    fireEvent.click(screen.getByText(/Settings/))
    await waitFor(() => expect(screen.queryAllByText(/Hello/).length).toBe(0))
})

it("hides the view panel on escape", async () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await userEvent.keyboard("{Escape}")
    await waitFor(() => expect(screen.queryAllByText(/Hello/).length).toBe(0))
})
