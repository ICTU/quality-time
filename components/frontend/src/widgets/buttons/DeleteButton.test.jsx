import { render } from "@testing-library/react"

import { expectText } from "../../testUtils"
import { DeleteButton } from "./DeleteButton"

test("DeleteButton has the correct label", () => {
    render(<DeleteButton itemType="bar" />)
    expectText(/bar/)
})
