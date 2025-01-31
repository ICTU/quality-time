import { render, screen } from "@testing-library/react"

import { Avatar } from "./Avatar"

it("shows the image when passed an email address", () => {
    render(<Avatar email="foo@bar" />)
    expect(screen.queryAllByAltText("Avatar for foo@bar").length).toBe(1)
    expect(screen.getByAltText("Avatar for foo@bar").getAttribute("src")).toEqual(
        "https://www.gravatar.com/avatar/cca210311c3caf70e4a335aad6fa1047?d=identicon",
    )
})
