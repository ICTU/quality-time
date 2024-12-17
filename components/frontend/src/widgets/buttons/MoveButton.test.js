import { act, fireEvent, render, screen } from "@testing-library/react"

import { MoveButton } from "./MoveButton"

Array("report", "subject", "metric", "source").forEach((itemType) => {
    test("MoveButton has the correct label", () => {
        render(<MoveButton itemType={itemType} />)
        expect(screen.getAllByText(new RegExp(`Move ${itemType}`)).length).toBe(1)
    })

    test("MoveButton can be used to select an item", async () => {
        const mockCallback = jest.fn()
        render(
            <MoveButton
                itemType={itemType}
                onChange={mockCallback}
                get_options={() => {
                    return [{ key: "1", text: "Item", value: "1" }]
                }}
            />,
        )
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Move ${itemType}`)))
        })
        await act(async () => {
            fireEvent.click(screen.getByText(/Item/))
        })
        expect(mockCallback).toHaveBeenCalledWith("1")
    })
})
