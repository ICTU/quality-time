import { render, screen } from "@testing-library/react"

import { MoveButton } from "./MoveButton"

Array("report", "subject", "metric", "source").forEach((itemType) => {
    test("MoveButton has the correct label", () => {
        render(<MoveButton itemType={itemType} get_options={() => []} />)
        expect(screen.getAllByText(new RegExp(`Move ${itemType}`)).length).toBe(1)
    })
})
