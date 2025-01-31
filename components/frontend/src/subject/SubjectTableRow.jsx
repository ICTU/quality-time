import { Chip, TableCell, Tooltip, Typography } from "@mui/material"
import { bool, func, number, object, string } from "prop-types"
import { useContext } from "react"

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
import {
    dataModelPropType,
    datePropType,
    datesPropType,
    directionPropType,
    measurementsPropType,
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
import { DivWithHTML } from "../widgets/DivWithHTML"
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
        return improved ? "success" : "error"
    }
    return "info"
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
            <Tooltip title={description}>
                <Chip color={color} label={delta} size="small" sx={{ borderRadius: 1 }} variant="outlined" />
            </Tooltip>
        )
    }
    return (
        <TableCell align="right" className={status}>
            {label}
        </TableCell>
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

function measurementOnDate(metric_uuid, measurements, date) {
    const isoDateString = date.toISOString().split("T")[0]
    return measurements?.find((m) => {
        return (
            m.metric_uuid === metric_uuid &&
            m.start.split("T")[0] <= isoDateString &&
            isoDateString <= m.end.split("T")[0]
        )
    })
}
measurementOnDate.propTypes = {
    metric_uuid: string,
    measurements: measurementsPropType,
    date: datePropType,
}

function metricValueAndStatusOnDate(dataModel, metric, metric_uuid, measurements, date) {
    const measurement = measurementOnDate(metric_uuid, measurements, date)
    const scale = getMetricScale(metric, dataModel)
    return [measurement?.[scale]?.value ?? "?", measurement?.[scale]?.status ?? "unknown"]
}
metricValueAndStatusOnDate.propTypes = {
    dataModel: dataModelPropType,
    metric: metricPropType,
    metric_uuid: string,
    measurements: measurementsPropType,
    date: datePropType,
}

function MeasurementCells({ dates, metric, metric_uuid, measurements, settings }) {
    const dataModel = useContext(DataModel)
    const showDeltaColumns = settings.hiddenColumns.excludes("delta")
    const dateOrderAscending = settings.dateOrder.value === "ascending"
    const scale = getMetricScale(metric, dataModel)
    const cells = []
    let previousValue = "?"
    dates.forEach((date, index) => {
        const [metricValue, status] = metricValueAndStatusOnDate(dataModel, metric, metric_uuid, measurements, date)
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
            <TableCell align="right" className={status} key={date}>
                {formatMetricValue(scale, metricValue)}
                {formatMetricScale(metric, dataModel)}
            </TableCell>,
        )
        previousValue = metricValue === "?" ? previousValue : metricValue
    })
    return cells
}
MeasurementCells.propTypes = {
    dates: datesPropType,
    measurements: measurementsPropType,
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
    const metricName = getMetricName(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const unit = getMetricUnit(metric, dataModel)
    const nrDates = dates.length
    return (
        <TableRowWithDetails
            className={nrDates === 1 ? metric.status || "unknown" : ""}
            color={nrDates === 1 ? metric.status || "unknown" : ""}
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
                />
            }
            expanded={settings.expandedItems.value.filter((item) => item?.startsWith(metric_uuid)).length > 0}
            id={metric_uuid}
            onExpand={(expand) => expandOrCollapseItem(expand, metric_uuid, settings.expandedItems)}
        >
            <TableCell>{metricName}</TableCell>
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
                <TableCell sx={{ width: "150px" }}>
                    <TrendSparkline measurements={metric.recent_measurements} report_date={reportDate} scale={scale} />
                </TableCell>
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("status") && (
                <TableCell>
                    <Typography sx={{ paddingLeft: "6px", fontSize: "24px" }}>
                        <StatusIcon status={metric.status} statusStart={metric.status_start} />
                    </Typography>
                </TableCell>
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("measurement") && (
                <TableCell align="right">
                    <MeasurementValue metric={metric} reportDate={reportDate} />
                </TableCell>
            )}
            {nrDates === 1 && settings.hiddenColumns.excludes("target") && (
                <TableCell align="right">
                    <MeasurementTarget metric={metric} />
                </TableCell>
            )}
            {settings.hiddenColumns.excludes("unit") && <TableCell>{unit}</TableCell>}
            {settings.hiddenColumns.excludes("source") && (
                <TableCell>
                    <MeasurementSources metric={metric} />
                </TableCell>
            )}
            {settings.hiddenColumns.excludes("time_left") && (
                <TableCell>
                    <TimeLeft metric={metric} report={report} />
                </TableCell>
            )}
            {nrDates > 1 && settings.hiddenColumns.excludes("overrun") && (
                <TableCell>
                    <Overrun
                        metric={metric}
                        metric_uuid={metric_uuid}
                        report={report}
                        measurements={measurements}
                        dates={dates}
                    />
                </TableCell>
            )}
            {settings.hiddenColumns.excludes("comment") && (
                <TableCell>
                    <DivWithHTML>{metric.comment}</DivWithHTML>
                </TableCell>
            )}
            {settings.hiddenColumns.excludes("issues") && (
                <TableCell>
                    <IssueStatus metric={metric} issueTrackerMissing={!report.issue_tracker} settings={settings} />
                </TableCell>
            )}
            {settings.hiddenColumns.excludes("tags") && (
                <TableCell>
                    {getMetricTags(metric).map((tag) => (
                        <Tag key={tag} tag={tag} />
                    ))}
                </TableCell>
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
    measurements: measurementsPropType,
    metric_uuid: string,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: measurementsPropType,
    settings: settingsPropType,
    subject_uuid: string,
}
