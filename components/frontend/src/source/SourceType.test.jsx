import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { SourceType } from "./SourceType"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi")
})

const dataModel = {
    metrics: {
        violations: {
            sources: ["sonarqube", "gitlab", "source_type"],
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count"],
        },
    },
    sources: {
        sonarqube: {
            name: "SonarQube",
            supported_versions_description: ">=8.2",
            documentation: { violations: "metric-specific documentation" },
        },
        gitlab: {
            name: "GitLab",
            deprecated: true,
            documentation: { generic: "generic documentation" },
        },
        unsupported: {
            name: "Unsupported",
        },
        source_type: {
            name: "Name differs from key",
        },
    },
}

async function renderSourceType(metricType, sourceType, mockSetSourceAttribute) {
    let result
    await act(async () => {
        result = render(
            <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                <DataModelContext value={dataModel}>
                    <SourceType
                        metricType={metricType}
                        sourceType={sourceType}
                        setSourceAttribute={mockSetSourceAttribute}
                    />
                </DataModelContext>
            </PermissionsContext>,
        )
    })
    return result
}

it("has no accessibility violations", async () => {
    const { container } = await renderSourceType("violations", "sonarqube")
    await expectNoAccessibilityViolations(container)
})

it("sets the source type", async () => {
    const mockSetSourceAttribute = vi.fn()
    await renderSourceType("violations", "sonarqube", mockSetSourceAttribute)
    await userEvent.type(screen.getByRole("combobox"), "GitLab{Enter}")
    expect(mockSetSourceAttribute).toHaveBeenLastCalledWith("type", "gitlab")
})

it("shows the metric type even when not supported by the subject type", async () => {
    await renderSourceType("violations", "unsupported")
    expectText(/Unsupported/)
})

it("shows the supported source versions", async () => {
    await renderSourceType("violations", "sonarqube")
    expectText(/Supported SonarQube versions: >=8.2/)
})

it("shows sources as deprecated if they are deprecated", async () => {
    await renderSourceType("violations", "sonarqube")
    fireEvent.mouseDown(screen.getByLabelText(/Source type/))
    expectText(/Deprecated/)
})

it("shows the source type read the docs URL", async () => {
    await renderSourceType("violations", "sonarqube")
    expectText(/Read the Docs/)
})

it("shows that the source type has extra generic documentation", async () => {
    await renderSourceType("violations", "gitlab")
    expectText(/additional information on how to configure this source type/)
})

it("shows that the source type has extra metric-specific documentation", async () => {
    await renderSourceType("violations", "sonarqube")
    expectText(/additional information on how to configure this source type/)
})

it("uses the name of the source type for the documentation link", async () => {
    await renderSourceType("violations", "source_type")
    const readTheDocsLink = screen.getByRole("link", { name: "Read the Docs" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#name-differs-from-key"))
})
