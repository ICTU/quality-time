import { render } from "@testing-library/react"

import { DivWithHtml } from "./DivWithHtml"

it("is not resizable when not overflown", () => {
    const { container } = render(
        <DivWithHtml>
            <p>Some text</p>
        </DivWithHtml>,
    )
    expect(container.firstChild).toHaveStyle("word-break: break-word; overflow: auto; min-height: 15px; height: 0px;")
})

it("is resizable when overflown", () => {
    // Fake a large text:
    Object.defineProperty(HTMLElement.prototype, "scrollHeight", { configurable: true, value: 500 })
    const { container } = render(
        <DivWithHtml>
            <p>Some text</p>
        </DivWithHtml>,
    )
    expect(container.firstChild).toHaveStyle(
        "word-break: break-word; overflow: auto; min-height: 15px; height: 60px; resize: vertical",
    )
})
