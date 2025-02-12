import { vi } from "vitest"

export function mockGetAnimations() {
    const originalGetElementById = document.getElementById
    document.getElementById = (id) => {
        const element = originalGetElementById.call(document, id)
        if (id === "dashboard" && element) {
            element.getAnimations = vi.fn().mockReturnValue([])
        }
        return element
    }
}
