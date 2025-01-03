import { render, screen } from "@testing-library/react"

import { SourceTypeHeader } from "./SourceTypeHeader"

function renderSourceTypeHeader(documentation, metricTypeId, deprecated) {
    render(
        <SourceTypeHeader
            metricTypeId={metricTypeId}
            sourceType={{
                name: "Source type",
                description: "Description",
                documentation: documentation,
                supported_versions_description: ">=1.0",
                deprecated: deprecated,
            }}
        />,
    )
}

it("shows the header", () => {
    renderSourceTypeHeader()
    expect(screen.getAllByText("Source type").length).toBe(1)
})

it("points users to specific information in the docs if there is", () => {
    renderSourceTypeHeader()
    expect(screen.queryAllByText(/specific information/).length).toBe(0)
    renderSourceTypeHeader({ generic: "Generic documentation" })
    expect(screen.getAllByText(/specific information/).length).toBe(1)
})

it("does not point users to specific information in the docs if the information is for other metric types", () => {
    renderSourceTypeHeader({ other_metric: "Generic documentation" })
    expect(screen.queryAllByText(/specific information/).length).toBe(0)
})

it("points users to specific information in the docs if the information is for the current metric type", () => {
    renderSourceTypeHeader({ metric_type: "Generic documentation" }, "metric_type")
    expect(screen.getAllByText(/specific information/).length).toBe(1)
})

it("shows the supported source versions", () => {
    renderSourceTypeHeader()
    expect(screen.getAllByText(/Supported Source type versions: >=1.0/).length).toBe(1)
})

it("does not show the source as deprecated if it is not deprecated", () => {
    renderSourceTypeHeader()
    expect(screen.queryAllByText(/Deprecated/).length).toBe(0)
})

it("shows the source as deprecated if it is deprecated", () => {
    renderSourceTypeHeader({}, null, true)
    expect(screen.getAllByText(/Deprecated/).length).toBe(1)
})
