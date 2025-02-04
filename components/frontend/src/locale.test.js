import { adapterLocale } from "./locale"

it("returns the default locale", () => {
    expect(adapterLocale("en")).toBe("en-GB")
})

it("returns the Dutch locale", () => {
    expect(adapterLocale("nl-NL")).toBe("nl")
})
