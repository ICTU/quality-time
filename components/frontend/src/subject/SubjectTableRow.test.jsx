import { Table, TableBody } from "@mui/material"
import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, render } from "@testing-library/react"
import history from "history/browser"

import { dataModel, report } from "../__fixtures__/fixtures"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    METRIC_CONFIGURATION_TAB_INDEX,
    METRIC_DEBT_TAB_INDEX,
    SOURCE_TAB_INDEX,
    SOURCES_TAB_INDEX,
    TREND_GRAPH_TAB_INDEX,
} from "../metric/MetricDetails"
import {
    asyncClickByTestId,
    asyncClickRole,
    asyncClickText,
    expectLabelText,
    expectNoAccessibilityViolations,
    expectNoLabelText,
    expectNoText,
    expectSearch,
    expectText,
} from "../testUtils"
import { SnackbarAlerts } from "../widgets/SnackbarAlerts"
import { SubjectTableRow } from "./SubjectTableRow"

beforeEach(() => history.push(""))

function SubjectTableRowWrapper({
    ascending,
    comment,
    direction,
    evaluateTargets,
    issueIds,
    name,
    scale,
    secondaryName,
    tags,
}) {
    const settings = useSettings()
    const dates = [new Date("2024-01-03"), new Date("2024-01-02"), new Date("2024-01-01")]
    if (ascending) {
        dates.reverse()
    }
    const reversedMeasurements = [
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
            count: { value: "11", status: "target_met" },
            version_number: { value: "1.0", status: "target_met" },
        },
    ]
    return (
        <Table>
            <TableBody>
                <SubjectTableRow
                    columnsToHide={[]}
                    dates={dates}
                    measurements={[]}
                    metric={{
                        comment: comment,
                        direction: direction,
                        evaluate_targets: evaluateTargets,
                        issue_ids: issueIds,
                        latest_measurement: { sources: [{ source_uuid: "source_uuid" }] },
                        name: name,
                        recent_measurements: [],
                        scale: scale,
                        secondary_name: secondaryName,
                        sources: { source_uuid: { type: "source_type", parameters: {} } },
                        status_start: "2024-01-03T00:00",
                        tags: tags,
                        type: "metric_type",
                        unit: "things",
                        unit_singular: "thing",
                    }}
                    metricUuid="metric_uuid"
                    report={report}
                    reversedMeasurements={reversedMeasurements}
                    settings={settings}
                    subjectUuid="subject_uuid"
                />
            </TableBody>
        </Table>
    )
}

function renderSubjectTableRow({
    comment = "",
    direction = "<",
    ascending = false,
    scale = "count",
    evaluateTargets = undefined,
    issueIds = undefined,
    permissions = "",
    name = "",
    secondaryName = "",
    tags = undefined,
} = {}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <PermissionsContext value={[permissions]}>
                <DataModelContext value={dataModel}>
                    <SnackbarAlerts messages={[]} showMessage={() => {}}>
                        <SubjectTableRowWrapper
                            ascending={ascending}
                            comment={comment}
                            direction={direction}
                            evaluateTargets={evaluateTargets}
                            issueIds={issueIds}
                            name={name}
                            scale={scale}
                            secondaryName={secondaryName}
                            tags={tags}
                        />
                    </SnackbarAlerts>
                </DataModelContext>
            </PermissionsContext>
        </LocalizationProvider>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSubjectTableRow()
    await expectNoAccessibilityViolations(container)
})

it("shows the delta column", async () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow()
    expectText("+1")
    expectLabelText("Metric type worsened from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type improved from 12 to 8 things by -4 things")
})

it("hides the delta column", async () => {
    history.push("?nr_dates=2&hidden_columns=delta")
    renderSubjectTableRow()
    expectNoText("+1")
    expectNoText("-4")
})

it("takes the metric direction into account", async () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow({ direction: ">" })
    expectText("+1")
    expectLabelText("Metric type improved from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type worsened from 12 to 8 things by -4 things")
})

it("works for informative metrics", async () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow({ evaluateTargets: false })
    expectText("+1")
    expectLabelText("Metric type changed from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type changed from 12 to 8 things by -4 things")
})

it("takes the date order into account", async () => {
    history.push("?nr_dates=3&date_interval=1&date_order=ascending")
    renderSubjectTableRow({ ascending: true })
    expectText("+1")
    expectLabelText("Metric type worsened from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type improved from 12 to 8 things by -4 things")
})

it("shows the delta column for the version scale", async () => {
    history.push("?nr_dates=3&date_interval=1")
    renderSubjectTableRow({ scale: "version_number" })
    expectText("+")
    expectLabelText("Metric type worsened from 1.0 to 1.2")
    expectText("-")
    expectLabelText("Metric type improved from 1.2 to 0.8")
})

it("shows the drag handle when row is not expanded and user is authenticated", () => {
    renderSubjectTableRow({ permissions: EDIT_REPORT_PERMISSION })
    expectLabelText("Drag to reorder")
})

it("shows no drag handle when row is expanded", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    await act(async () => {
        renderSubjectTableRow()
    })
    expectNoLabelText("Drag to reorder")
})

it("shows no drag handle when rows are sorted", () => {
    history.push("?sort_column=metric")
    renderSubjectTableRow({ permissions: EDIT_REPORT_PERMISSION })
    expectNoLabelText("Drag to reorder")
})

it("shows the metric type as name if the metric has no name", async () => {
    renderSubjectTableRow()
    expectText("Metric type")
})

it("shows the metric name", async () => {
    renderSubjectTableRow({ name: "Metric name" })
    expectText("Metric name")
})

it("shows the metric secondary name", async () => {
    renderSubjectTableRow({ secondaryName: "Secondary name" })
    expectText("Secondary name")
})

it("expands the metric on the configuration tab when the metric name is clicked", async () => {
    renderSubjectTableRow({ name: "Metric name" })
    await asyncClickText(/Metric name/, 0)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("switches to the configuration tab when the metric name is clicked on an expanded row with a different tab", async () => {
    history.push("?expanded=metric_uuid:1")
    renderSubjectTableRow({ name: "Metric name" })
    await asyncClickText(/Metric name/, 0)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("collapses the metric when the metric name is clicked on an expanded row with the configuation tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow({ name: "Metric name" })
    await asyncClickText(/Metric name/, 0)
    expectSearch("")
})

it("collapses the metric when the expand button is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${TREND_GRAPH_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("button", /expand\/collapse/i)
    expectSearch("")
})

it("expands the metric on the technical debt tab when the status is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickByTestId("QuestionMarkIcon")
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("switches to the technical debt tab when the status is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickByTestId("QuestionMarkIcon")
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("collapses the metric when the status is clicked on an expanded row with the technical debt tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_DEBT_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickByTestId("QuestionMarkIcon")
    expectSearch("")
})

it("expands the metric on the trend graph tab when the sparkline is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickRole("cell", /sparkline graph showing 0 different measurement values in the week before today/)
    expectSearch(`?expanded=metric_uuid%3A${TREND_GRAPH_TAB_INDEX}`)
})

it("switches to the trend graph tab when the sparkline is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("cell", /sparkline graph showing 0 different measurement values in the week before today/)
    expectSearch(`?expanded=metric_uuid%3A${TREND_GRAPH_TAB_INDEX}`)
})

it("collapses the metric when the sparkline is clicked on an expanded row with the trend graph tab active", async () => {
    history.push(`?expanded=metric_uuid:${TREND_GRAPH_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("cell", /sparkline graph showing 0 different measurement values in the week before today/)
    expectSearch("")
})

it("expands the metric on the first source tab when the measurement value is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickRole("cell", "?")
    expectSearch(`?expanded=metric_uuid%3A${SOURCE_TAB_INDEX}`)
})

it("switches to the source tab when the measurement value is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("cell", "?")
    expectSearch(`?expanded=metric_uuid%3A${SOURCE_TAB_INDEX}`)
})

it("collapses the metric when the measurement value is clicked on an expanded row with the source tab active", async () => {
    history.push(`?expanded=metric_uuid:${SOURCE_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("cell", "?")
    expectSearch("")
})

it("expands the metric on the configuration tab when the target value is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickRole("cell", "≦ 0")
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("switches to the configuration tab when the measurement target is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${SOURCE_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("cell", "≦ 0")
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("collapses the metric when the measurement target is clicked on an expanded row with the configuration tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickRole("cell", "≦ 0")
    expectSearch("")
})

it("expands the metric on the configuration tab when the unit is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickText(/things/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("switches to the configuration tab when the unit is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${SOURCE_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickText(/things/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("collapses the metric when the unit is clicked on an expanded row with the configuration tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickText(/things/)
    expectSearch("")
})

it("expands the metric on the technical debt tab when the time left is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickText(/days/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("switches to the technical debt tab when the time left is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickText(/days/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("collapses the metric when the time left is clicked on an expanded row with the technical debt tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_DEBT_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickText(/days/)
    expectSearch("")
})

it("expands the metric on the technical debt tab when the comment is clicked", async () => {
    renderSubjectTableRow({ comment: "Metric comment" })
    await asyncClickText("Metric comment")
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("switches to the technical debt tab when the comment is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${SOURCE_TAB_INDEX}`)
    renderSubjectTableRow({ comment: "Metric comment" })
    await asyncClickText("Metric comment")
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("collapses the metric when the comment is clicked on an expanded row with the technical debt tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_DEBT_TAB_INDEX}`)
    renderSubjectTableRow({ comment: "Metric comment" })
    await asyncClickText("Metric comment")
    expectSearch("")
})

it("expands the metric on the technical debt tab when the issues are clicked", async () => {
    renderSubjectTableRow({ issueIds: ["ABC-1"] })
    await asyncClickText(/ABC-1/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("switches to the technical debt tab when the issues are clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${SOURCE_TAB_INDEX}`)
    renderSubjectTableRow({ issueIds: ["ABC-1"] })
    await asyncClickText(/ABC-1/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_DEBT_TAB_INDEX}`)
})

it("collapses the metric when the issues are clicked on an expanded row with the technical debt tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_DEBT_TAB_INDEX}`)
    renderSubjectTableRow({ issueIds: ["ABC-1"] })
    await asyncClickText(/ABC-1/)
    expectSearch("")
})

it("expands the metric on the sources tab when the source is clicked", async () => {
    renderSubjectTableRow()
    await asyncClickText(/Source type name/)
    expectSearch(`?expanded=metric_uuid%3A${SOURCES_TAB_INDEX}`)
})

it("switches to the sources tab when the source is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickText(/Source type name/)
    expectSearch(`?expanded=metric_uuid%3A${SOURCES_TAB_INDEX}`)
})

it("collapses the metric when the source is clicked on an expanded row with the sources tab active", async () => {
    history.push(`?expanded=metric_uuid:${SOURCES_TAB_INDEX}`)
    renderSubjectTableRow()
    await asyncClickText(/Source type name/, 0)
    expectSearch("")
})

it("expands the metric on the configuration tab when a tag is clicked", async () => {
    renderSubjectTableRow({ tags: ["tag1"] })
    await asyncClickText(/tag1/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("switches to the configuration tab when a tag is clicked on an expanded row with a different tab", async () => {
    history.push(`?expanded=metric_uuid:${SOURCE_TAB_INDEX}`)
    renderSubjectTableRow({ tags: ["tag1"] })
    await asyncClickText(/tag1/)
    expectSearch(`?expanded=metric_uuid%3A${METRIC_CONFIGURATION_TAB_INDEX}`)
})

it("collapses the metric when a tag is clicked on an expanded row with the configuration tab active", async () => {
    history.push(`?expanded=metric_uuid:${METRIC_CONFIGURATION_TAB_INDEX}`)
    renderSubjectTableRow({ tags: ["tag1"] })
    await asyncClickText(/tag1/)
    expectSearch("")
})
