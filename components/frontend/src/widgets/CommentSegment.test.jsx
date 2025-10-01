import { render } from "@testing-library/react"

import { expectText } from "../testUtils"
import { CommentSegment } from "./CommentSegment"

it("shows the comment", () => {
    render(<CommentSegment comment="Comment" />)
    expectText(/Comment/)
})

it("doesn't show the comment if it's empty", () => {
    const { container } = render(<CommentSegment />)
    expect(container.children.length).toBe(0)
})
