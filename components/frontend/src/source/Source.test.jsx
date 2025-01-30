import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { Source } from "./Source"

vi.mock("../api/fetch_server_api.js")

const dataModel = {
    metrics: {
        metric_type: { sources: ["source_type1", "source_type2"] },
        unsupported_metric: { sources: [] },
    },
    sources: {
        source_type1: { name: "Source type 1", parameters: {} },
        source_type2: { name: "Source type 2", parameters: {} },
    },
}
const source = { type: "source_type1" }
const metric = { type: "metric_type", sources: { source_uuid: source } }
const report = { report_uuid: "report_uuid", subjects: {} }

function renderSource(metric, props) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Source metric={metric} report={report} source_uuid="source_uuid" {...props} />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("invokes the callback on clicking delete", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSource(metric)
    fireEvent.click(screen.getByText(/Delete source/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "delete", "source/source_uuid", {})
    await expectNoAccessibilityViolations(container)
})

it("changes the source type", async () => {
    const { container } = renderSource(metric)
    fireEvent.mouseDown(screen.getByLabelText(/Source type/))
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByText(/Source type 2/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/attribute/type", {
        type: "source_type2",
    })
})

it("changes the source name", async () => {
    renderSource(metric)
    await userEvent.type(screen.getByLabelText(/Source name/), "New source name{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/attribute/name", {
        name: "New source name",
    })
})

it("shows a connection error message", async () => {
    const { container } = renderSource(metric, { measurement_source: { connection_error: "Oops" } })
    expect(screen.getAllByText(/Connection error/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a parse error message", async () => {
    const { container } = renderSource(metric, { measurement_source: { parse_error: "Oops" } })
    expect(screen.getAllByText(/Parse error/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a config error message", async () => {
    const { container } = renderSource({ type: "unsupported_metric", sources: { source_uuid: source } })
    expect(screen.getAllByText(/Configuration error/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("loads the changelog", async () => {
    const { container } = renderSource(metric)
    await act(async () => {
        fireEvent.click(screen.getByText(/Changelog/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/source/source_uuid/5")
    await expectNoAccessibilityViolations(container)
})
