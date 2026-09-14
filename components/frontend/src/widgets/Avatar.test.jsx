import { render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { expectAltTextAfterWait, expectNoAltText } from "../testUtils"
import { Avatar } from "./Avatar"

const fooAtBarUrl =
    "https://gravatar.com/avatar/eb6a491e2c7bb5af04c19c487c0e9b85f933b6d73404863cc094d960e332b607?d=identicon"

afterEach(() => {
    vi.unstubAllGlobals()
})

async function expectAvatarSrc(alt, src) {
    await expectAltTextAfterWait(alt)
    expect(screen.getByAltText(alt).getAttribute("src")).toEqual(src)
}

it("shows the image when passed an email address", async () => {
    render(<Avatar email="foo@bar" />)
    await expectAvatarSrc("Avatar for foo@bar", fooAtBarUrl)
})

it("ignores case and surrounding whitespace in the email address", async () => {
    render(<Avatar email=" FOO@BAR " />)
    await expectAvatarSrc("Avatar for FOO@BAR", fooAtBarUrl) // Testing library normalizes whitespace when matching
})

it("shows the image when not passed an email address", async () => {
    render(<Avatar />)
    await expectAvatarSrc(
        "Avatar for undefined",
        "https://gravatar.com/avatar/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855?d=identicon",
    )
})

it("shows no image when the Web Crypto API is not available", () => {
    vi.stubGlobal("crypto", {}) // The Web Crypto API is only available in secure contexts
    render(<Avatar email="foo@bar" />)
    expectNoAltText("Avatar for foo@bar")
})
