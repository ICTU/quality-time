import { array, bool, func, number, object, string } from "prop-types"
import { useContext } from "react"

import { DarkMode } from "../context/DarkMode"
import { DataModel } from "../context/DataModel"
import { IssueStatus } from "../issue/IssueStatus"
import { MeasurementSources } from "../measurement/MeasurementSources"
import { MeasurementTarget } from "../measurement/MeasurementTarget"
import { MeasurementValue } from "../measurement/MeasurementValue"
import { Overrun } from "../measurement/Overrun"
import { StatusIcon } from "../measurement/StatusIcon"
import { TimeLeft } from "../measurement/TimeLeft"
import { TrendSparkline } from "../measurement/TrendSparkline"
import { MetricDetails } from "../metric/MetricDetails"
import { Label, Popup, Table } from "../semantic_ui_react_wrappers"
import {
    datesPropType,
    directionPropType,
    metricPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    scalePropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import {
    formatMetricScale,
    formatMetricScaleAndUnit,
    formatMetricValue,
    getMetricDirection,
    getMetricName,
    getMetricScale,
    getMetricTags,
    getMetricUnit,
} from "../utils"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { Tag } from "../widgets/Tag"

function didValueIncrease(dateOrderAscending, metricValue, previousValue, scale) {
    let value = metricValue
    let previous = previousValue
    if (scale !== "version_number") {
        value = Number(metricValue)
        previous = Number(previousValue)
    }
    return (dateOrderAscending && value > previous) || (!dateOrderAscending && value < previous)
}
didValueIncrease.propTypes = {
    dateOrderAscending: bool,
    metricValue: string,
    previousValue: string,
    scale: scalePropType,
}

function didValueImprove(didValueIncrease, direction) {
    return (didValueIncrease && direction === ">") || (!didValueIncrease && direction === "<")
}
didValueImprove.propTypes = {
    didValueIncrease: bool,
    direction: directionPropType,
}

function deltaColor(metric, improved) {
    const evaluateTarget = metric.evaluate_targets ?? true
    if (evaluateTarget) {
        return improved ? "green" : "red"
    }
    return "blue"
}
deltaColor.propTypes = {
    metric: metricPropType,
    improved: bool,
}

function deltaDescription(dataModel, metric, scale, delta, improved, oldValue, newValue) {
    let description = `${getMetricName(metric, dataModel)} `
    const evaluateTarget = metric.evaluate_targets ?? true
    if (evaluateTarget) {
        description += improved ? "improved" : "worsened"
    } else {
        description += `changed`
    }
    description += ` from ${formatMetricValue(scale, oldValue)} to ${formatMetricValue(scale, newValue)}`
    if (scale !== "version_number") {
        const unit = formatMetricScaleAndUnit(metric, dataModel)
        description += `${unit} by ${delta}${unit}`
    }
    return description
}
deltaDescription.propTypes = {
    dataModel: object,
    metric: metricPropType,
    scale: string,
    delta: string,
    improved: bool,
    oldValue: string,
    newValue: string,
}

function deltaLabel(increased, scale, metricValue, previousValue) {
    let delta = increased ? "+" : "-"
    if (scale !== "version_number") {
        delta += `${formatMetricValue(scale, Math.abs(metricValue - previousValue))}`
    }
    return delta
}
deltaLabel.propTypes = {
    increased: bool,
    scale: string,
    metricValue: string,
    previousValue: string,
}

function DeltaCell({ dateOrderAscending, index, metric, metricValue, previousValue, status }) {
    const dataModel = useContext(DataModel)
    let label = null
    if (index > 0 && previousValue !== "?" && metricValue !== "?" && previousValue !== metricValue) {
        // Note that the delta cell only gets content if the previous and current values are both available and unequal
        const scale = getMetricScale(metric, dataModel)
        const increased = didValueIncrease(dateOrderAscending, metricValue, previousValue, scale)
        const delta = deltaLabel(increased, scale, metricValue, previousValue)
        const oldValue = dateOrderAscending ? previousValue : metricValue
        const newValue = dateOrderAscending ? metricValue : previousValue
        const direction = getMetricDirection(metric, dataModel)
        const improved = didValueImprove(increased, direction)
        const description = deltaDescription(dataModel, metric, scale, delta, improved, oldValue, newValue)
        const color = deltaColor(metric, improved)
        label = (
            <Popup
                content={description}
                trigger={
                    <Label aria-label={description} basic color={color}>
                        {delta}
                    </Label>
                }
            />
        )
    }
    return (
        <Table.Cell className={status} singleLine textAlign="right">
            {label}
        </Table.Cell>
    )
}
DeltaCell.propTypes = {
    dateOrderAscending: bool,
    metric: metricPropType,
    index: number,
    metricValue: string,
    previousValue: string,
    status: string,
}

function MeasurementCells({ dates, metric, metric_uuid, measurements, settings }) {
    const dataModel = useContext(DataModel)
    const showDeltaColumns = settings.hiddenColumns.excludes("delta")
    const dateOrderAscending = settings.dateOrder.value === "ascending"
    const scale = getMetricScale(metric, dataModel)
    const cells = []
    let previousValue = "?"
    dates.forEach((date, index) => {
        const isoDateString = date.toISOString().split("T")[0]
        const measurement = measurements?.find((m) => {
            return (
                m.metric_uuid === metric_uuid &&
                m.start.split("T")[0] <= isoDateString &&
                isoDateString <= m.end.split("T")[0]
            )
        })
        let metricValue = measurement?.[scale]?.value ?? "?"
        const status = measurement?.[scale]?.status ?? "unknown"
        if (showDeltaColumns && index > 0) {
            cells.push(
                <DeltaCell
                    dateOrderAscending={dateOrderAscending}
                    index={index}
                    key={`${date}-delta`}
                    metric={metric}
                    metricValue={metricValue}
                    previousValue={previousValue}
                    status={status}
                />,
            )
        }
        cells.push(
            <Table.Cell className={status} key={date} textAlign="right">
                {formatMetricValue(scale, metricValue)}
                {formatMetricScale(metric, dataModel)}
            </Table.Cell>,
        )
        previousValue = metricValue === "?" ? previousValue : metricValue
    })
    return cells
}
MeasurementCells.propTypes = {
    dates: datesPropType,
    measurements: array,
    metric_uuid: string,
    metric: metricPropType,
    settings: settingsPropType,
}

function expandOrCollapseItem(expand, metric_uuid, expandedItems) {
    if (expand) {
        expandedItems.toggle(`${metric_uuid}:0`)
    } else {
        const items = expandedItems.value.filter((each) => each?.startsWith(metric_uuid))
        expandedItems.toggle(items[0])
    }
}

export function SubjectTableRow({
    changed_fields,
    dates,
    handleSort,
    index,
    lastIndex,
    measurements,
    metric_uuid,
    metric,
    reload,
    report,
    reportDate,
    reports,
    reversedMeasurements,
    settings,
    subject_uuid,
}) {
    const dataModel = useContext(DataModel)
    const darkMode = useContext(DarkMode)
    const metricName = getMetricName(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const unit = getMetricUnit(metric, dataModel)
    const nrDates = dates.length
    const style = nrDates > 1 ? { background: darkMode ? "rgba(60, 60, 60, 1)" : "#f9fafb" } : {}
    return (
        <TableRowWithDetails
            className={nrDates === 1 ? metric.status || "unknown" : ""}
            details={
                <MetricDetails
                    changed_fields={changed_fields}
                    first_metric={index === 0}
                    last_metric={index === lastIndex}
                    metric_uuid={metric_uuid}
                    reload={reload}
                    report_date={reportDate}
                    reports={reports}
                    report={report}
                    stopFilteringAndSorting={() => {
                        handleSort(null)
                        settings.hiddenTags.reset()
                        settings.metricsToHide.reset()
                    }}
                    subject_uuid={subject_uuid}
                    expandedItems={settings.expandedItems}
                />
            }
            expanded={settings.expandedItems.value.filter((item) => item?.startsWith(metric_uuid)).length > 0}
            id={metric_uuid}
            onExpand={(expand) => expandOrCollapseItem(expand, metric_uuid, settings.expandedItems)}
            style={style}
        >
            <Table.Cell style={style}>{metricName}</Table.Cell>
            {nrDates > 1 && (
                <MeasurementCells
                    dates={dates}
                    metric={metric}
                    metric_uuid={metric_uuid}
                    measurements={reversedMeasurements}
                    settings={settings}
                />
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("trend") && (
                <Table.Cell>
                    <TrendSparkline measurements={metric.recent_measurements} report_date={reportDate} scale={scale} />
                </Table.Cell>
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("status") && (
                <Table.Cell textAlign="center">
                    <StatusIcon status={metric.status} status_start={metric.status_start} />
                </Table.Cell>
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("measurement") && (
                <Table.Cell textAlign="right">
                    <MeasurementValue metric={metric} reportDate={reportDate} />
                </Table.Cell>
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("target") && (
                <Table.Cell textAlign="right">
                    <MeasurementTarget metric={metric} />
                </Table.Cell>
            )}
            {settings.hiddenColumns.excludes("unit") && <Table.Cell style={style}>{unit}</Table.Cell>}
            {settings.hiddenColumns.excludes("source") && (
                <Table.Cell style={style}>
                    <MeasurementSources metric={metric} />
                </Table.Cell>
            )}
            {settings.hiddenColumns.excludes("time_left") && (
                <Table.Cell style={style}>
                    <TimeLeft metric={metric} report={report} />
                </Table.Cell>
            )}
            {nrDates > 1 && settings.hiddenColumns.excludes("overrun") && (
                <Table.Cell style={style}>
                    <Overrun
                        metric={metric}
                        metric_uuid={metric_uuid}
                        report={report}
                        measurements={measurements}
                        dates={dates}
                    />
                </Table.Cell>
            )}
            {settings.hiddenColumns.excludes("comment") && (
                <Table.Cell style={style}>
                    <div style={{ wordBreak: "break-word" }} dangerouslySetInnerHTML={{ __html: metric.comment }} />
                </Table.Cell>
            )}
            {settings.hiddenColumns.excludes("issues") && (
                <Table.Cell style={style}>
                    <IssueStatus metric={metric} issueTrackerMissing={!report.issue_tracker} settings={settings} />
                </Table.Cell>
            )}
            {settings.hiddenColumns.excludes("tags") && (
                <Table.Cell style={style}>
                    {getMetricTags(metric).map((tag) => (
                        <Tag key={tag} tag={tag} />
                    ))}
                </Table.Cell>
            )}
        </TableRowWithDetails>
    )
}
SubjectTableRow.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    index: number,
    lastIndex: number,
    measurements: array,
    metric_uuid: string,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: array,
    settings: settingsPropType,
    subject_uuid: string,
}
