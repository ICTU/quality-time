import { render, screen } from "@testing-library/react"

import { AddButton } from "./AddButton"

test("AddButton has the correct label", () => {
    render(<AddButton itemType="bar" />)
    expect(screen.getAllByText(/bar/).length).toBe(1)
})
