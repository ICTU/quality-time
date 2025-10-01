import { render } from "@testing-library/react"
import { vi } from "vitest"

import { asyncClickButton, clickButton } from "../../testUtils"
import { ReorderButtonGroup } from "./ReorderButtonGroup"

Array("first", "last", "previous", "next").forEach((direction) => {
    test("ReorderButtonGroup calls the callback on click direction", async () => {
        const mockCallback = vi.fn()
        render(<ReorderButtonGroup onClick={mockCallback} moveable="item" />)
        await asyncClickButton(`Move item to the ${direction} position`)
        expect(mockCallback).toHaveBeenCalledWith(direction)
    })

    test("ReorderButtonGroup does not call the callback on click direction when the button group is already there", () => {
        const mockCallback = vi.fn()
        render(<ReorderButtonGroup onClick={mockCallback} first={true} last={true} moveable="item" />)
        clickButton(`Move item to the ${direction} position`)
        expect(mockCallback).not.toHaveBeenCalled()
    })
})
