import { renderHook } from "@testing-library/react"
import history from "history/browser"

import { useSettings } from "../app_ui_settings"
import { determineColumnsToHide } from "./subject_column"

beforeEach(() => history.push(""))

function testableSettings() {
    return renderHook(() => useSettings()).result.current
}

it("determines the columns to hide with one date", async () => {
    const columnsToHide = determineColumnsToHide({}, [], [], 1, {}, testableSettings())
    expect(columnsToHide).toEqual(["overrun"])
})

it("determines the columns to hide with multiple dates", async () => {
    const columnsToHide = determineColumnsToHide({}, [], [], 2, {}, testableSettings())
    expect(columnsToHide).toEqual(["measurement", "status", "target", "trend"])
})

it("determines the columns to hide when a column is explicitly hidden", async () => {
    history.push("?hidden_columns=hidden")
    const columnsToHide = determineColumnsToHide({}, [], [], 1, {}, testableSettings())
    expect(columnsToHide).toEqual(["hidden", "overrun"])
})

it("determines empty columns to hide", async () => {
    history.push("?hide_empty_columns=true")
    const columnsToHide = determineColumnsToHide({}, [], [], 1, {}, testableSettings())
    expect(columnsToHide).toEqual(["comment", "issues", "overrun", "tags", "time_left"])
})
