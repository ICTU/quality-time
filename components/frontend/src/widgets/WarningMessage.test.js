import { render, screen } from "@testing-library/react"

import { WarningMessage } from "./WarningMessage"

it("shows a warning message if showIf is true", () => {
    render(<WarningMessage header="Warning" showIf={true} />)
    expect(screen.getAllByText("Warning").length).toBe(1)
})

it("does not show a warning message if showIf is false", () => {
    render(<WarningMessage header="Warning" showIf={false} />)
    expect(screen.queryAllByText("Warning").length).toBe(0)
})

it("shows a warning message if showIf is undefined", () => {
    render(<WarningMessage header="Warning" />)
    expect(screen.getAllByText("Warning").length).toBe(1)
})
