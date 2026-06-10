import { render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    asyncClickText,
    expectFetch,
    expectLabelText,
    expectNoAccessibilityViolations,
    expectNoText,
    expectText,
} from "../testUtils"
import { SourceLocations } from "./SourceLocations"

beforeEach(() => {
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

const reportWithoutSourceLocations = { report_uuid: "report_uuid", subjects: {} }

function SourceLocationsWrapper({ permissions, theReport }) {
    const settings = useSettings()
    return (
        <PermissionsContext value={permissions}>
            <DataModelContext value={dataModel}>
                <SourceLocations reload={vi.fn()} report={theReport} settings={settings} />
            </DataModelContext>
        </PermissionsContext>
    )
}

function renderSourceLocations({ permissions = [EDIT_REPORT_PERMISSION], theReport = report } = {}) {
    return render(<SourceLocationsWrapper permissions={permissions} theReport={theReport} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceLocations()
    await expectNoAccessibilityViolations(container)
})

it("shows a message if there are no source locations", async () => {
    const { container } = renderSourceLocations({ theReport: reportWithoutSourceLocations })
    expectText(/No source locations have been configured yet/)
    await expectNoAccessibilityViolations(container)
})

it("shows the source location name, source type, URL, and number of sources using the source location", async () => {
    renderSourceLocations()
    expectText("Source location 1")
    expectText("Source type name")
    expectText("https://source.org")
    expectText("2")
})

it("shows the source type name as source location name if the source location has no name", async () => {
    const theReport = {
        report_uuid: "report_uuid",
        source_locations: { source_location_uuid: { source_type: "source_type", url: "https://source.org" } },
        subjects: {},
    }
    renderSourceLocations({ theReport: theReport })
    expectText("Source type name", 2) // Once in the source location column and once in the source type column
})

it("does not show the source location details when the source location is not expanded", async () => {
    renderSourceLocations()
    expectLabelText("Expand/collapse")
    expect(screen.queryAllByLabelText(/Source location name/).length).toBe(0)
})

it("shows the source location details when the source location is expanded", async () => {
    history.push("?expanded=source_location_uuid:0")
    const { container } = renderSourceLocations()
    expectLabelText(/Source location name/)
    await expectNoAccessibilityViolations(container)
})

it("adds a source location", async () => {
    renderSourceLocations({ theReport: reportWithoutSourceLocations })
    await asyncClickText(/Add source location/)
    await asyncClickText("Source type name")
    expectFetch("post", "source_location/new/report_uuid", { type: "source_type" })
})

it("only offers source types that have source locations", async () => {
    renderSourceLocations({ theReport: reportWithoutSourceLocations })
    await asyncClickText(/Add source location/)
    expectText("Source type name")
    expectNoText("Source type without location parameters")
})

it("does not show the add source location button without permissions", async () => {
    renderSourceLocations({ permissions: [] })
    expectNoText(/Add source location/)
})

it("disables the delete button when the source location is used by sources", async () => {
    history.push("?expanded=source_location_uuid:0")
    const { container } = renderSourceLocations()
    expect(screen.getByText(/Delete source location/).closest("button")).toBeDisabled()
    await expectNoAccessibilityViolations(container)
})

it("deletes the source location when it is not used by any source", async () => {
    history.push("?expanded=source_location_uuid:0")
    const theReport = { ...report, subjects: {} }
    renderSourceLocations({ theReport: theReport })
    const deleteButton = screen.getByText(/Delete source location/).closest("button")
    expect(deleteButton).toBeEnabled()
    await asyncClickText(/Delete source location/)
    expectFetch("delete", "source_location/source_location_uuid", {})
})

it("does not show the delete button without permissions", async () => {
    history.push("?expanded=source_location_uuid:0")
    renderSourceLocations({ permissions: [] })
    expectNoText(/Delete source location/)
})
