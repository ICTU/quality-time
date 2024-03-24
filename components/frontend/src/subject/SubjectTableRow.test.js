import { render, screen } from "@testing-library/react"
import history from "history/browser"
import { Table } from "../semantic_ui_react_wrappers"
import { DataModel } from "../context/DataModel"
import { SubjectTableRow } from "./SubjectTableRow"
import { createTestableSettings, datamodel, report } from "../__fixtures__/fixtures"

beforeEach(() => {
    history.push("")
})

function renderSubjectTableRow({
    direction = "<",
    ascending = false,
    scale = "count",
    evaluate_targets = undefined,
} = {}) {
    const dates = [new Date("2024-01-03"), new Date("2024-01-02"), new Date("2024-01-01")]
    const reverseMeasurements = [
        {
            metric_uuid: "metric_uuid",
            start: "2024-01-03T00:00",
            end: "2024-01-03T00:00",
            count: { value: "8", status: "target_met" },
            version_number: { value: "0.8", status: "target_met" },
        },
        {
            metric_uuid: "metric_uuid",
            start: "2024-01-02T00:00",
            end: "2024-01-02T00:00",
            count: { value: "12", status: "target_met" },
            version_number: { value: "1.2", status: "target_met" },
        },
        {
            metric_uuid: "metric_uuid",
            start: "2024-01-01T00:00",
            end: "2024-01-01T00:00",
            count: { value: "10", status: "target_met" },
            version_number: { value: "1.0", status: "target_met" },
        },
    ]
    if (ascending) {
        dates.reverse()
    }
    render(
        <DataModel.Provider value={datamodel}>
            <Table>
                <Table.Body>
                    <SubjectTableRow
                        dates={dates}
                        measurements={[]}
                        metric={{
                            direction: direction,
                            evaluate_targets: evaluate_targets,
                            recent_measurements: [],
                            scale: scale,
                            type: "metric_type",
                            unit: "things",
                        }}
                        metric_uuid="metric_uuid"
                        report={report}
                        reversedMeasurements={reverseMeasurements}
                        settings={createTestableSettings()}
                    />
                </Table.Body>
            </Table>
        </DataModel.Provider>,
    )
}

it("shows the delta column", () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow()
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type worsened from 10 to 12 things by +2 things").length,
    ).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type improved from 12 to 8 things by -4 things").length,
    ).toBe(1)
})

it("hides the delta column", () => {
    history.push("?nr_dates=2&hidden_columns=delta")
    renderSubjectTableRow()
    expect(screen.queryAllByText("+2").length).toBe(0)
})

it("takes the metric direction into account", () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow({ direction: ">" })
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type improved from 10 to 12 things by +2 things").length,
    ).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type worsened from 12 to 8 things by -4 things").length,
    ).toBe(1)
})

it("works for informative metrics", () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow({ evaluate_targets: false })
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type changed from 10 to 12 things by +2 things").length,
    ).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type changed from 12 to 8 things by -4 things").length,
    ).toBe(1)
})

it("takes the date order into account", () => {
    history.push("?nr_dates=3&date_interval=1&date_order=ascending")
    renderSubjectTableRow({ ascending: true })
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type worsened from 10 to 12 things by +2 things").length,
    ).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(
        screen.getAllByLabelText("Metric type improved from 12 to 8 things by -4 things").length,
    ).toBe(1)
})

it("shows the delta column for the version scale", () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow({ scale: "version_number" })
    expect(screen.getAllByText("+").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type worsened from 1.0 to 1.2").length).toBe(1)
    expect(screen.getAllByText("-").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type improved from 1.2 to 0.8").length).toBe(1)
})
