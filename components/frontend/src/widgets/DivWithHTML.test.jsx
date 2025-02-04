import { render } from "@testing-library/react"

import { DivWithHTML } from "./DivWithHTML"

it("is not resizable when not overflown", () => {
    const { container } = render(
        <DivWithHTML>
            <p>Some text</p>
        </DivWithHTML>,
    )
    expect(container.firstChild).toHaveStyle("word-break: break-word; overflow: auto; min-height: 15px; height: 0px;")
})

it("is resizable when overflown", () => {
    // Fake a large text:
    Object.defineProperty(HTMLElement.prototype, "scrollHeight", { configurable: true, value: 500 })
    const { container } = render(
        <DivWithHTML>
            <p>Some text</p>
        </DivWithHTML>,
    )
    expect(container.firstChild).toHaveStyle(
        "word-break: break-word; overflow: auto; min-height: 15px; height: 60px; resize: vertical",
    )
})
