import { act, fireEvent, render, screen, within } from "@testing-library/react"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { expectFetch, expectNoAccessibilityViolations, expectText } from "../testUtils"
import { SourceLocationSelect } from "./SourceLocationSelect"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

const dataModel = {
    sources: {
        source_type: { name: "Source type", parameters: { url: { name: "URL", type: "url" } } },
        other_source_type: { name: "Other source type", parameters: { url: { name: "URL", type: "url" } } },
        calendar: { name: "Calendar", parameters: {} },
    },
}

const report = {
    source_locations: {
        source_location_uuid: {
            location_name: "Location 1",
            source_type: "source_type",
            url: "https://location1",
        },
        other_source_location_uuid: {
            location_name: "Location 2",
            source_type: "other_source_type",
            url: "https://location2",
        },
    },
}

function renderSourceLocationSelect({
    permissions = [EDIT_REPORT_PERMISSION],
    source = { type: "source_type" },
    theReport = report,
} = {}) {
    return render(
        <PermissionsContext value={permissions}>
            <DataModelContext value={dataModel}>
                <SourceLocationSelect reload={vi.fn()} report={theReport} source={source} sourceUuid="source_uuid" />
            </DataModelContext>
        </PermissionsContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceLocationSelect()
    await expectNoAccessibilityViolations(container)
})

it("renders nothing for source types without location parameters", async () => {
    const { container } = renderSourceLocationSelect({ source: { type: "calendar" } })
    expect(container).toBeEmptyDOMElement()
})

it("shows an info message when the report has no source locations for the source type", async () => {
    renderSourceLocationSelect({ theReport: {} })
    expectText(/No source locations/)
    expectText(/Expand the report title and add a source location in the 'Source locations' tab./)
})

it("shows the name of the selected source location", async () => {
    renderSourceLocationSelect({ source: { type: "source_type", source_location: "source_location_uuid" } })
    expectText("Location 1")
})

it("shows the source type name and the URL of the source locations", async () => {
    renderSourceLocationSelect()
    fireEvent.mouseDown(screen.getByLabelText(/Source location/))
    const listbox = within(screen.getByRole("listbox"))
    expect(listbox.getAllByText("Location 1").length).toBe(1)
    expect(listbox.getAllByText("Source type - https://location1").length).toBe(1)
})

it("only lists source locations with the same source type as the source", async () => {
    renderSourceLocationSelect()
    fireEvent.mouseDown(screen.getByLabelText(/Source location/))
    const listbox = within(screen.getByRole("listbox"))
    expect(listbox.getAllByText("Location 1").length).toBe(1)
    expect(listbox.queryAllByText("Location 2").length).toBe(0)
})

it("sets the source location of the source", async () => {
    renderSourceLocationSelect()
    fireEvent.mouseDown(screen.getByLabelText(/Source location/))
    const listbox = within(screen.getByRole("listbox"))
    await act(async () => fireEvent.click(listbox.getByText("Location 1")))
    expectFetch("post", "source/source_uuid/attribute/source_location", {
        source_location: "source_location_uuid",
    })
})
