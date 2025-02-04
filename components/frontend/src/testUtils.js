import { act } from "@testing-library/react"
import { axe } from "jest-axe"

export async function expectNoAccessibilityViolations(container) {
    jest.useRealTimers()
    await act(async () => expect(await axe(container)).toHaveNoViolations())
}
