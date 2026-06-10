import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { expectFetch, expectLabelText, expectNoAccessibilityViolations, expectNoLabelText } from "../testUtils"
import { SourceLocationParameters } from "./SourceLocationParameters"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

const dataModel = {
    sources: {
        source_type: {
            name: "Source type",
            parameters: {
                url: { name: "URL", type: "url", mandatory: true },
                landing_url: { name: "Landing page URL", type: "url" },
                username: { name: "Username", type: "string" },
                password: { name: "Password", type: "password" },
                private_token: { name: "Private token", type: "password" },
                branch: { name: "Branch", type: "string" },
            },
        },
    },
}

function renderSourceLocationParameters({
    fieldWithUrlAvailabilityError = null,
    permissions = [EDIT_REPORT_PERMISSION],
    sourceLocation = { source_type: "source_type", url: "https://source" },
} = {}) {
    return render(
        <PermissionsContext value={permissions}>
            <DataModelContext value={dataModel}>
                <SourceLocationParameters
                    fieldWithUrlAvailabilityError={fieldWithUrlAvailabilityError}
                    reload={vi.fn()}
                    sourceLocation={sourceLocation}
                    sourceLocationUuid="source_location_uuid"
                />
            </DataModelContext>
        </PermissionsContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceLocationParameters()
    await expectNoAccessibilityViolations(container)
})

it("renders the source location name field and the location parameters of the source type", async () => {
    renderSourceLocationParameters()
    expectLabelText(/Source location name/)
    expectLabelText(/^URL/)
    expectLabelText(/Landing page URL/)
    expectLabelText(/Username/)
    expectLabelText(/Password/)
    expectLabelText(/Private token/)
})

it("does not render parameters that are not location parameters", async () => {
    renderSourceLocationParameters()
    expectNoLabelText(/Branch/)
})

it("sets the source location name", async () => {
    renderSourceLocationParameters()
    await userEvent.type(screen.getByLabelText(/Source location name/), "New name{Enter}")
    expectFetch("post", "source_location/source_location_uuid/attribute/location_name", { location_name: "New name" })
})

it("sets the url parameter", async () => {
    renderSourceLocationParameters()
    await userEvent.type(screen.getByLabelText(/^URL/), "/new{Enter}")
    expectFetch("post", "source_location/source_location_uuid/parameter/url", { url: "https://source/new" })
})

it("sets the username parameter", async () => {
    renderSourceLocationParameters()
    await userEvent.type(screen.getByLabelText(/Username/), "janedoe{Enter}")
    expectFetch("post", "source_location/source_location_uuid/parameter/username", { username: "janedoe" })
})

it("renders the password and private token parameters as password fields", async () => {
    renderSourceLocationParameters()
    expect(screen.getByLabelText(/Password/)).toHaveAttribute("type", "password")
    expect(screen.getByLabelText(/Private token/)).toHaveAttribute("type", "password")
})

it("renders the url field as invalid when the url is not available", async () => {
    renderSourceLocationParameters({
        fieldWithUrlAvailabilityError: { source_uuid: "source_location_uuid", parameter_key: "url" },
    })
    expect(screen.getByLabelText(/^URL/)).toBeInvalid()
})

it("renders the url field as valid when the url is available", async () => {
    renderSourceLocationParameters({
        fieldWithUrlAvailabilityError: { source_uuid: "source_location_uuid", parameter_key: "landing_url" },
    })
    expect(screen.getByLabelText(/^URL/)).toBeValid()
})

it("disables the fields without permissions", async () => {
    renderSourceLocationParameters({ permissions: [] })
    expect(screen.getByLabelText(/Source location name/)).toBeDisabled()
    expect(screen.getByLabelText(/^URL/)).toBeDisabled()
})
