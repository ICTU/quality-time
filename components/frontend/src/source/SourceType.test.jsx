import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SourceType } from "./SourceType"

vi.mock("../api/fetch_server_api.js")

const dataModel = {
    metrics: {
        violations: {
            sources: ["sonarqube", "gitlab"],
            unit: "violations",
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
    },
}

async function renderSourceType(metricType, sourceType, mockSetSourceAttribute) {
    let result
    await act(async () => {
        result = render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={dataModel}>
                    <SourceType
                        metric_type={metricType}
                        source_type={sourceType}
                        set_source_attribute={mockSetSourceAttribute}
                    />
                </DataModel.Provider>
            </Permissions.Provider>,
        )
    })
    return result
}

it("sets the source type", async () => {
    const mockSetSourceAttribute = vi.fn()
    const { container } = await renderSourceType("violations", "sonarqube", mockSetSourceAttribute)
    await userEvent.type(screen.getByRole("combobox"), "GitLab{Enter}")
    expect(mockSetSourceAttribute).toHaveBeenLastCalledWith("type", "gitlab")
    await expectNoAccessibilityViolations(container)
})

it("shows the metric type even when not supported by the subject type", async () => {
    const { container } = await renderSourceType("violations", "unsupported")
    expect(screen.getAllByText(/Unsupported/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the supported source versions", async () => {
    const { container } = await renderSourceType("violations", "sonarqube")
    expect(screen.getAllByText(/Supported SonarQube versions: >=8.2/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows sources as deprecated if they are deprecated", async () => {
    const { container } = await renderSourceType("violations", "sonarqube")
    fireEvent.mouseDown(screen.getByLabelText(/Source type/))
    expect(screen.getAllByText(/Deprecated/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the source type read the docs URL", async () => {
    const { container } = await renderSourceType("violations", "sonarqube")
    expect(screen.getAllByText(/Read the Docs/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows that the source type has extra generic documentation", async () => {
    const { container } = await renderSourceType("violations", "gitlab")
    expect(screen.getAllByText(/additional information on how to configure this source type/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows that the source type has extra metric-specific documentation", async () => {
    const { container } = await renderSourceType("violations", "sonarqube")
    expect(screen.getAllByText(/additional information on how to configure this source type/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
