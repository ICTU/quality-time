import { render } from "@testing-library/react"

import { expectText } from "../../testUtils"
import { MoveButton } from "./MoveButton"

Array("report", "subject", "metric", "source").forEach((itemType) => {
    test("MoveButton has the correct label", () => {
        render(<MoveButton itemType={itemType} getOptions={() => []} />)
        expectText(new RegExp(`Move ${itemType}`))
    })
})
