import { renderHook } from "@testing-library/react"
import { vi } from "vitest"

import { useHashFragment } from "./hash_fragment"

beforeEach(() => {
    vi.useFakeTimers()
})

afterEach(() => {
    vi.useRealTimers()
})

it("does not scroll if trigger is false", () => {
    window.addEventListener = vi.fn()
    const mockScrollIntoView = vi.fn()
    document.getElementById = () => {
        return { scrollIntoView: mockScrollIntoView }
    }
    renderHook(() => useHashFragment(false))
    expect(vi.getTimerCount()).toBe(0)
    expect(mockScrollIntoView).not.toHaveBeenCalled()
})

it("does not scroll if trigger is true but no element found", () => {
    window.addEventListener = vi.fn()
    document.getElementById = () => {
        return null
    }
    const { unmount } = renderHook(() => useHashFragment(true))
    expect(vi.getTimerCount()).toBe(1)
    vi.advanceTimersByTime(100)
    unmount()
    expect(vi.getTimerCount()).toBe(0)
})

it("does scroll if trigger is true and element found", () => {
    window.addEventListener = vi.fn()
    const mockScrollIntoView = vi.fn()
    document.getElementById = () => {
        return { scrollIntoView: mockScrollIntoView }
    }
    const { unmount } = renderHook(() => useHashFragment(true))
    expect(vi.getTimerCount()).toBe(1)
    vi.advanceTimersByTime(100)
    unmount()
    expect(vi.getTimerCount()).toBe(0)
    expect(mockScrollIntoView).toHaveBeenCalled()
})
