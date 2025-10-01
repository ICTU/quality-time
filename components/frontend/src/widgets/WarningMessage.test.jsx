import { render } from "@testing-library/react"

import { expectNoText, expectText } from "../testUtils"
import { WarningMessage } from "./WarningMessage"

it("shows a warning message if showIf is true", () => {
    render(<WarningMessage showIf={true}>Warning</WarningMessage>)
    expectText("Warning")
})

it("does not show a warning message if showIf is false", () => {
    render(<WarningMessage showIf={false}>Warning</WarningMessage>)
    expectNoText("Warning")
})

it("shows a warning message if showIf is undefined", () => {
    render(<WarningMessage>Warning</WarningMessage>)
    expectText("Warning")
})
