import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { determineColumnsToHide } from "./source_entity_column"

beforeEach(() => history.push(""))

it("determines the columns to hide if empty columns are not hidden", async () => {
    const columnsToHide = determineColumnsToHide(createTestableSettings(), {}, [])
    expect(columnsToHide).toEqual([])
})

it("determines the columns to hide if empty columns are hidden", async () => {
    history.push("?hide_empty_columns=true")
    const columnsToHide = determineColumnsToHide(createTestableSettings(), {}, [{}])
    expect(columnsToHide).toEqual(["rationale", "status_end_date"])
})

it("determines the columns to hide if empty columns are hidden and the columns are not empty", async () => {
    history.push("?hide_empty_columns=true")
    const columnsToHide = determineColumnsToHide(
        createTestableSettings(),
        { entity_user_data: { entity_key: { rationale: "rationale", status_end_date: "2026-01-01" } } },
        [{ key: "entity_key" }],
    )
    expect(columnsToHide).toEqual([])
})
