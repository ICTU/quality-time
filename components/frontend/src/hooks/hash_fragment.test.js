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
    globalThis.addEventListener = vi.fn()
    globalThis.location = { hash: "#d57aa11f-9bbb-4297-91e6-062e20c0a953" }
    const mockScrollIntoView = vi.fn()
    document.getElementById = () => {
        return { scrollIntoView: mockScrollIntoView }
    }
    renderHook(() => useHashFragment(false))
    expect(vi.getTimerCount()).toBe(0)
    expect(mockScrollIntoView).not.toHaveBeenCalled()
})

it("does not scroll if trigger is true but no hash is present", () => {
    globalThis.addEventListener = vi.fn()
    globalThis.location = { hash: "" }
    const mockScrollIntoView = vi.fn()
    document.getElementById = () => {
        return { scrollIntoView: mockScrollIntoView }
    }
    renderHook(() => useHashFragment(true))
    expect(vi.getTimerCount()).toBe(0)
    expect(mockScrollIntoView).not.toHaveBeenCalled()
})

it("does not scroll if trigger is true and hash is present, but element does not appear", () => {
    globalThis.addEventListener = vi.fn()
    globalThis.location = { hash: "#d57aa11f-9bbb-4297-91e6-062e20c0a954" }
    document.getElementById = () => {
        return null
    }
    const { unmount } = renderHook(() => useHashFragment(true))
    expect(vi.getTimerCount()).toBe(1)
    vi.advanceTimersByTime(100)
    unmount()
    expect(vi.getTimerCount()).toBe(0)
})

it("does scroll if trigger is true, hash is present, and element does appear", () => {
    globalThis.addEventListener = vi.fn()
    globalThis.location = { hash: "#d57aa11f-9bbb-4297-91e6-062e20c0a955" }
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
