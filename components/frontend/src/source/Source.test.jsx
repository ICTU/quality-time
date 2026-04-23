import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { clickText, expectFetch, expectNoAccessibilityViolations, expectText } from "../testUtils"
import { Source } from "./Source"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
    history.push("")
})

afterEach(() => vi.clearAllMocks())

const dataModel = {
    metrics: {
        metric_type: { name: "Metric type 1", sources: ["source_type1", "source_type2"] },
        unsupported_metric: { name: "Metric type 2", sources: [] },
    },
    sources: {
        source_type1: { name: "Source type 1", parameters: {} },
        source_type2: { name: "Source type 2", parameters: {} },
    },
}
const source = { type: "source_type1" }
const metric = { type: "metric_type", sources: { source_uuid: source } }
const report = { report_uuid: "report_uuid", subjects: {} }

function SourceWrapper({ metric, props }) {
    const settings = useSettings()
    return (
        <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
            <DataModelContext value={dataModel}>
                <Source metric={metric} report={report} settings={settings} sourceUuid="source_uuid" {...props} />
            </DataModelContext>
        </PermissionsContext>
    )
}

function renderSource(metric, props) {
    return render(<SourceWrapper metric={metric} props={props} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderSource(metric)
    await expectNoAccessibilityViolations(container)
})

it("invokes the callback on clicking delete", async () => {
    renderSource(metric)
    clickText(/Delete source/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(1, "delete", "source/source_uuid", {})
})

it("changes the source type", async () => {
    renderSource(metric)
    fireEvent.mouseDown(screen.getByLabelText(/Source type/))
    clickText(/Source type 2/)
    expectFetch("post", "source/source_uuid/attribute/type", { type: "source_type2" })
})

it("changes the source name", async () => {
    renderSource(metric)
    await userEvent.type(screen.getByLabelText(/Source name/), "New source name{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 100,
    })
    expectFetch("post", "source/source_uuid/attribute/name", { name: "New source name" })
})

it("shows a connection error message", async () => {
    renderSource(metric, { measurementSource: { connection_error: "Oops" } })
    expectText(/Connection error/)
})

it("shows a parse error message", async () => {
    renderSource(metric, { measurementSource: { parse_error: "Oops" } })
    expectText(/Parse error/)
})

it("shows a config error message", async () => {
    renderSource({ type: "unsupported_metric", sources: { source_uuid: source } })
    expectText(/Configuration error/)
})

it("shows an info message", async () => {
    renderSource(metric, { measurementSource: { info_message: "Some info" } })
    expectText(/Note/)
})

it("loads the changelog", async () => {
    history.push("?expanded=source_uuid:1")
    renderSource(metric)
    await act(async () => expectFetch("get", "changelog/source/source_uuid/5"))
})
