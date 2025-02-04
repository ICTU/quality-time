import { fireEvent, render, screen } from "@testing-library/react"

import { HyperLink } from "./HyperLink"

it("shows the hyperlink", () => {
    render(<HyperLink url="https://url">Link</HyperLink>)
    expect(screen.queryAllByText("Link").length).toBe(1)
})

it("does not propagate a click event", () => {
    const eventHandler = jest.fn()
    render(
        <button onClick={() => eventHandler()}>
            <HyperLink url="https://url">Link</HyperLink>
        </button>,
    )
    fireEvent.click(screen.getByText(/Link/))
    expect(eventHandler).not.toHaveBeenCalled()
})
