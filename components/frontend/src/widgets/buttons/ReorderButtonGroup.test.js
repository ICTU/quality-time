import { act, fireEvent, render, screen } from "@testing-library/react"

import { ReorderButtonGroup } from "./ReorderButtonGroup"

Array("first", "last", "previous", "next").forEach((direction) => {
    test("ReorderButtonGroup calls the callback on click direction", async () => {
        const mockCallback = jest.fn()
        render(<ReorderButtonGroup onClick={mockCallback} moveable="item" />)
        await act(async () => {
            fireEvent.click(screen.getByRole("button", { name: `Move item to the ${direction} position` }))
        })
        expect(mockCallback).toHaveBeenCalledWith(direction)
    })

    test("ReorderButtonGroup does not call the callback on click direction when the button group is already there", () => {
        const mockCallback = jest.fn()
        render(<ReorderButtonGroup onClick={mockCallback} first={true} last={true} moveable="item" />)
        fireEvent.click(screen.getByRole("button", { name: `Move item to the ${direction} position` }))
        expect(mockCallback).not.toHaveBeenCalled()
    })
})
