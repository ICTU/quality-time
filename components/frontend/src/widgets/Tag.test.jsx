import { render } from "@testing-library/react"

import { Tag } from "./Tag"

it("has the default color when not selected", () => {
    const { container } = render(<Tag tag="tag" />)
    expect(container.firstChild.className).toEqual(expect.stringContaining("MuiChip-color "))
})

it("has the primary color when selected", () => {
    const { container } = render(<Tag selected tag="tag" />)
    expect(container.firstChild.className).toEqual(expect.stringContaining("MuiChip-colorPrimary"))
})
