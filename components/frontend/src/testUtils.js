import { act } from "@testing-library/react"
import { axe } from "jest-axe"
import { vi } from "vitest"

export async function expectNoAccessibilityViolations(container) {
    vi.useRealTimers()
    await act(async () => expect(await axe(container)).toHaveNoViolations())
}
