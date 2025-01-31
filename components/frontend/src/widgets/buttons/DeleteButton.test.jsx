import { render, screen } from "@testing-library/react"

import { DeleteButton } from "./DeleteButton"

test("DeleteButton has the correct label", () => {
    render(<DeleteButton itemType="bar" />)
    expect(screen.getAllByText(/bar/).length).toBe(1)
})
