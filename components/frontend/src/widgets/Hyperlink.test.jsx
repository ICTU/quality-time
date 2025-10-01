import { render } from "@testing-library/react"
import { vi } from "vitest"

import { clickText, expectText } from "../testUtils"
import { HyperLink } from "./HyperLink"

it("shows the hyperlink", () => {
    render(<HyperLink url="https://url">Link</HyperLink>)
    expectText("Link")
})

it("does not propagate a click event", () => {
    const eventHandler = vi.fn()
    render(
        <button onClick={() => eventHandler()}>
            <HyperLink url="https://url">Link</HyperLink>
        </button>,
    )
    clickText(/Link/)
    expect(eventHandler).not.toHaveBeenCalled()
})
