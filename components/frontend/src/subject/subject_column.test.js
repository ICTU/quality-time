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

it("does not hide non-empty columns when hide_empty_columns is on", async () => {
    history.push("?hide_empty_columns=true")
    const metric = {
        comment: "a comment",
        issue_ids: ["ISSUE-1"],
        tags: ["tag1"],
        status_start: "2020-01-01T00:00:00Z",
        scale: "count",
    }
    const columnsToHide = determineColumnsToHide({}, [], [["m1", metric]], 1, {}, testableSettings())
    expect(columnsToHide).toEqual(["overrun"])
})

it("does not hide the overrun column when overruns exist", async () => {
    history.push("?hide_empty_columns=true")
    const metric = { status_start: "2020-01-01T00:00:00Z", scale: "count" }
    const measurements = [
        {
            metric_uuid: "m1",
            count: { status: "target_not_met" },
            start: "2020-01-01T00:00:00Z",
            end: "2020-12-31T00:00:00Z",
        },
    ]
    const columnsToHide = determineColumnsToHide({}, measurements, [["m1", metric]], 2, {}, testableSettings())
    // overrun is absent because there's a non-zero overrun; time_left is absent because status_start is set
    expect(columnsToHide).toEqual(["comment", "issues", "measurement", "status", "tags", "target", "trend"])
})
