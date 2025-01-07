import { render, screen } from "@testing-library/react"

import { WarningMessage } from "./WarningMessage"

it("shows a warning message if showIf is true", () => {
    render(<WarningMessage showIf={true}>Warning</WarningMessage>)
    expect(screen.getAllByText("Warning").length).toBe(1)
})

it("does not show a warning message if showIf is false", () => {
    render(<WarningMessage showIf={false}>Warning</WarningMessage>)
    expect(screen.queryAllByText("Warning").length).toBe(0)
})

it("shows a warning message if showIf is undefined", () => {
    render(<WarningMessage>Warning</WarningMessage>)
    expect(screen.getAllByText("Warning").length).toBe(1)
})
