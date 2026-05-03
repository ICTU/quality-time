import { render, screen } from "@testing-library/react"

import { expectAltText } from "../testUtils"
import { Avatar } from "./Avatar"

it("shows the image when passed an email address", () => {
    render(<Avatar email="foo@bar" />)
    expectAltText("Avatar for foo@bar")
    expect(screen.getByAltText("Avatar for foo@bar").getAttribute("src")).toEqual(
        "https://www.gravatar.com/avatar/cca210311c3caf70e4a335aad6fa1047?d=identicon",
    )
})
