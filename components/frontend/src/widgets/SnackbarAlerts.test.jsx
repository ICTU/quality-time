import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { clickRole, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { SnackbarAlerts } from "./SnackbarAlerts"

beforeEach(() => {
    history.push("")
})

afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
})

function renderSnackbarAlerts({
    messages = [{ severity: "info", title: "Info", description: "Some info" }],
    hideMessage = vi.fn(),
} = {}) {
    return render(<SnackbarAlerts messages={messages} hideMessage={hideMessage} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderSnackbarAlerts()
    await expectNoAccessibilityViolations(container)
})

it("shows no messages by default", () => {
    renderSnackbarAlerts({ messages: [] })
    expectNoText(/info/)
})

it("shows a message", () => {
    renderSnackbarAlerts()
    expectText(/Info/)
})

it("automatically calls the hide message callback", () => {
    const hideMessage = vi.fn()
    vi.useFakeTimers()
    renderSnackbarAlerts({ hideMessage: hideMessage })
    act(() => vi.advanceTimersByTime(50000))
    expect(hideMessage).toHaveBeenCalledTimes(1)
})

it("calls the hide message callback on click close", () => {
    const hideMessage = vi.fn()
    renderSnackbarAlerts({ hideMessage: hideMessage })
    clickRole("button", "Close")
    expect(hideMessage).toHaveBeenCalledTimes(1)
})

it("hides messages immediately if messages should not be shown at all", () => {
    history.push("?hide_toasts=true")
    renderSnackbarAlerts()
    expectNoText(/Info/)
})

it("does not hide a message when hovering it", async () => {
    const hideMessage = vi.fn()
    renderSnackbarAlerts({ hideMessage: hideMessage })
    fireEvent.mouseEnter(screen.getByRole("alert"))
    vi.useFakeTimers()
    await act(async () => await vi.advanceTimersByTimeAsync(50000))
    expect(hideMessage).not.toHaveBeenCalled()
})

it("does hide message after hovering it", async () => {
    const hideMessage = vi.fn()
    renderSnackbarAlerts({ hideMessage: hideMessage })
    fireEvent.mouseEnter(screen.getByRole("alert"))
    vi.useFakeTimers()
    await act(async () => await vi.advanceTimersByTimeAsync(10000))
    fireEvent.mouseLeave(screen.getByRole("alert"))
    await act(async () => await vi.advanceTimersByTimeAsync(50000))
    expect(hideMessage).toHaveBeenCalledTimes(1)
})

it("does not hide a message when clicking away", async () => {
    const hideMessage = vi.fn()
    render(
        <>
            <p data-testid="away">Click away here</p>
            <SnackbarAlerts
                messages={[{ severity: "info", title: "Some info", description: "Some info" }]}
                hideMessage={hideMessage}
            />
        </>,
    )
    // ClickAwayListener activates asynchronously via setTimeout(..., 0); wait a tick.
    await act(async () => await new Promise((resolve) => setTimeout(resolve, 0)))
    fireEvent.click(screen.getByTestId("away"))
    expect(hideMessage).not.toHaveBeenCalled()
})
