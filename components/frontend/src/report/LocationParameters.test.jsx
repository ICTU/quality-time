import { render } from "@testing-library/react"
import { vi } from "vitest"

import { dataModel } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { enterLabeledText, expectFetch, expectText } from "../testUtils"
import { SnackbarAlerts } from "../widgets/SnackbarAlerts"
import { LocationParameters } from "./LocationParameters"

function renderLocationParameters({ source, sourceUuid = "source_uuid", showMessage, theDataModel } = {}) {
    return render(
        <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
            <DataModelContext value={theDataModel ?? dataModel}>
                <SnackbarAlerts messages={[]} showMessage={showMessage ?? vi.fn()}>
                    <LocationParameters
                        reload={vi.fn()}
                        report={{ subjects: {} }}
                        source={source}
                        sourceUuid={sourceUuid}
                    />
                </SnackbarAlerts>
            </DataModelContext>
        </PermissionsContext>,
    )
}

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

it("shows a message for sources without location parameters", async () => {
    renderLocationParameters({ source: { type: "source_type_without_location_parameters", parameters: {} } })
    expectText(/This source has no location parameters/)
})

it("changes the value of a parameter of a source without parameter layout", async () => {
    const showMessage = vi.fn()
    renderLocationParameters({
        source: { type: "source_type", parameters: { url: "https://source.org" } },
        showMessage,
    })
    await enterLabeledText(/URL/, "/new")
    expectFetch("post", "source/source_uuid/parameter/url", { url: "https://source.org/new", edit_scope: "report" })
    expect(showMessage).not.toHaveBeenCalled()
})

it("mass changes the value of a parameter", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true, nr_sources_mass_edited: 2 })
    const showMessage = vi.fn()
    renderLocationParameters({
        source: { type: "source_type", parameters: { url: "https://source.org" } },
        showMessage,
    })
    await enterLabeledText(/URL/, "/new")
    expectFetch("post", "source/source_uuid/parameter/url", { url: "https://source.org/new", edit_scope: "report" })
    expect(showMessage).toHaveBeenCalledWith({
        description: "Changed 2 sources",
        severity: "info",
        title: "Mass edit",
    })
})

it("changes the value of a parameter of a source with parameter layout", async () => {
    const showMessage = vi.fn()
    const theDataModel = { ...dataModel }
    theDataModel.sources["source_type"].parameters = {
        api_version: { name: "API version", type: "string" },
    }
    theDataModel.sources["source_type"].parameter_layout = {
        location: { parameters: ["api_version"] },
    }
    renderLocationParameters({
        source: { type: "source_type", parameters: { api_version: "2" } },
        showMessage,
        theDataModel,
    })
    await enterLabeledText(/API version/, "{Backspace}3")
    expectFetch("post", "source/source_uuid/parameter/api_version", { api_version: "3", edit_scope: "report" })
    expect(showMessage).not.toHaveBeenCalled()
})
