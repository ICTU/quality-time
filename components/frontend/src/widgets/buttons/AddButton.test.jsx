import { render } from "@testing-library/react"

import { expectText } from "../../testUtils"
import { AddButton } from "./AddButton"

test("AddButton has the correct label", () => {
    render(<AddButton itemType="bar" />)
    expectText(/bar/)
})
