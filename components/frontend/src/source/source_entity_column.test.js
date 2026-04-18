import { renderHook } from "@testing-library/react"
import history from "history/browser"

import { useSettings } from "../app_ui_settings"
import { determineColumnsToHide } from "./source_entity_column"

beforeEach(() => history.push(""))

function testableSettings() {
    return renderHook(() => useSettings()).result.current
}

it("determines the columns to hide if empty columns are not hidden", async () => {
    const columnsToHide = determineColumnsToHide(testableSettings(), {}, [])
    expect(columnsToHide).toEqual([])
})

it("determines the columns to hide if empty columns are hidden", async () => {
    history.push("?hide_empty_columns=true")
    const columnsToHide = determineColumnsToHide(testableSettings(), {}, [{}])
    expect(columnsToHide).toEqual(["rationale", "status_end_date"])
})

it("determines the columns to hide if empty columns are hidden and the columns are not empty", async () => {
    history.push("?hide_empty_columns=true")
    const columnsToHide = determineColumnsToHide(
        testableSettings(),
        { entity_user_data: { entity_key: { rationale: "rationale", status_end_date: "2026-01-01" } } },
        [{ key: "entity_key" }],
    )
    expect(columnsToHide).toEqual([])
})
