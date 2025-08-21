import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { determineColumnsToHide } from "./subject_column"

beforeEach(() => history.push(""))

it("determines the columns to hide with one date", async () => {
    const columnsToHide = determineColumnsToHide({}, [], [], 1, {}, createTestableSettings())
    expect(columnsToHide).toEqual(["overrun"])
})

it("determines the columns to hide with multiple dates", async () => {
    const columnsToHide = determineColumnsToHide({}, [], [], 2, {}, createTestableSettings())
    expect(columnsToHide).toEqual(["measurement", "status", "target", "trend"])
})

it("determines the columns to hide when a column is explicitly hidden", async () => {
    history.push("?hidden_columns=hidden")
    const settings = createTestableSettings()
    const columnsToHide = determineColumnsToHide({}, [], [], 1, {}, settings)
    expect(columnsToHide).toEqual(["hidden", "overrun"])
})

it("determines empty columns to hide", async () => {
    history.push("?hide_empty_columns=true")
    const settings = createTestableSettings()
    const columnsToHide = determineColumnsToHide({}, [], [], 1, {}, settings)
    expect(columnsToHide).toEqual(["comment", "issues", "overrun", "tags", "time_left"])
})
