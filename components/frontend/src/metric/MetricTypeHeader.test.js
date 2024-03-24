import { render, screen } from "@testing-library/react"
import { MetricTypeHeader } from "./MetricTypeHeader"

function renderMetricTypeHeader(documentation) {
    render(
        <MetricTypeHeader
            metricType={{
                name: "Metric type",
                description: "Description",
                documentation: documentation,
            }}
        />,
    )
}

it("shows the header", () => {
    renderMetricTypeHeader()
    expect(screen.getAllByText("Metric type").length).toBe(1)
})

it("points users to specific information in the docs if there is", () => {
    renderMetricTypeHeader()
    expect(screen.queryAllByText(/specific information/).length).toBe(0)
    renderMetricTypeHeader("Metric docs")
    expect(screen.getAllByText(/specific information/).length).toBe(1)
})
