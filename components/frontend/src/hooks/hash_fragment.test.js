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
    vi.advanceTimersByTime(100)
    expect(mockScrollIntoView).not.toHaveBeenCalled()
    expect(window.addEventListener).not.toHaveBeenCalled()
})

it("does not scroll if trigger is true but no element found", () => {
    window.addEventListener = vi.fn()
    document.getElementById = () => {
        return null
    }
    renderHook(() => useHashFragment(true))
    vi.advanceTimersByTime(100)
    expect(window.addEventListener).toHaveBeenCalled()
})

it("does scroll if trigger is true and element found", () => {
    window.addEventListener = vi.fn()
    const mockScrollIntoView = vi.fn()
    document.getElementById = () => {
        return { scrollIntoView: mockScrollIntoView }
    }
    renderHook(() => useHashFragment(true))
    vi.advanceTimersByTime(100)
    expect(mockScrollIntoView).toHaveBeenCalled()
    expect(window.addEventListener).toHaveBeenCalled()
})
