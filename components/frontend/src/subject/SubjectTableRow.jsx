import DragIndicatorIcon from "@mui/icons-material/DragIndicator"
import { Chip, TableCell, Tooltip, Typography } from "@mui/material"
import { bool, func, number, object, string } from "prop-types"
import React, { useContext, useRef } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { IssueStatus } from "../issue/IssueStatus"
import { MeasurementSources } from "../measurement/MeasurementSources"
import { MeasurementTarget } from "../measurement/MeasurementTarget"
import { MeasurementValue } from "../measurement/MeasurementValue"
import { Overrun } from "../measurement/Overrun"
import { StatusIcon } from "../measurement/StatusIcon"
import { TimeLeft } from "../measurement/TimeLeft"
import { TrendSparkline } from "../measurement/TrendSparkline"
import { MetricDetails } from "../metric/MetricDetails"
import { measurementOnDate } from "../report/report_utils"
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
import { DivWithHtml } from "../widgets/DivWithHtml"
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

function DeltaCell({ dateOrderAscending, index, metric, metricValue, previousValue }) {
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
    return <TableCell align="right">{label}</TableCell>
}
DeltaCell.propTypes = {
    dateOrderAscending: bool,
    metric: metricPropType,
    index: number,
    metricValue: string,
    previousValue: string,
}

function metricValueAndStatusOnDate(dataModel, metric, metricUuid, measurements, date) {
    const measurement = measurementOnDate(date, measurements, metricUuid)
    const scale = getMetricScale(metric, dataModel)
    return [measurement?.[scale]?.value ?? "?", measurement?.[scale]?.status ?? "unknown"]
}
metricValueAndStatusOnDate.propTypes = {
    dataModel: dataModelPropType,
    metric: metricPropType,
    metricUuid: string,
    measurements: measurementsPropType,
    date: datePropType,
}

function MeasurementCells({ dates, metric, metricUuid, measurements, settings }) {
    const dataModel = useContext(DataModel)
    const showDeltaColumns = settings.hiddenColumns.excludes("delta")
    const dateOrderAscending = settings.dateOrder.value === "ascending"
    const scale = getMetricScale(metric, dataModel)
    const cells = []
    let previousValue = "?"
    dates.forEach((date, index) => {
        const [metricValue, status] = metricValueAndStatusOnDate(dataModel, metric, metricUuid, measurements, date)
        if (showDeltaColumns && index > 0) {
            cells.push(
                <DeltaCell
                    dateOrderAscending={dateOrderAscending}
                    index={index}
                    key={`${date}-delta`}
                    metric={metric}
                    metricValue={metricValue}
                    previousValue={previousValue}
                />,
            )
        }
        cells.push(
            <TableCell
                align="right"
                key={date}
                sx={{
                    bgcolor: `${status}.bgcolor`,
                    "&.MuiTableCell-hover": {
                        "&:hover": {
                            backgroundColor: `${status}.hover`,
                        },
                    },
                }}
            >
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
    metricUuid: string,
    metric: metricPropType,
    settings: settingsPropType,
}

const DragHandleButton = React.forwardRef(function DragHandleButton({ label, ...props }, ref) {
    return (
        <button
            ref={ref}
            type="button"
            {...props}
            style={{
                background: "none",
                border: "none",
                cursor: "grab",
                padding: 0,
            }}
            aria-label={label}
        >
            <DragIndicatorIcon fontSize="small" />
        </button>
    )
})
DragHandleButton.propTypes = {
    label: string,
}

export function SubjectTableRow({
    changedFields,
    columnsToHide,
    dates,
    handleSort,
    index,
    lastIndex,
    measurements,
    metricUuid,
    metric,
    reload,
    report,
    reportDate,
    reports,
    reversedMeasurements,
    settings,
    subjectUuid,
    onDragStart,
    onDragEnter,
    onDrop,
    isDropTarget,
}) {
    const dataModel = useContext(DataModel)
    const metricName = getMetricName(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const unit = getMetricUnit(metric, dataModel)
    const nrDates = dates.length

    const rowRef = useRef(null)
    const dragHandleRef = useRef(null)

    const anyRowExpanded = settings.expandedItems.value.length > 0

    return (
        <TableRowWithDetails
            data-testid={`metric-row-${index}`}
            ref={rowRef}
            onDragEnter={() => onDragEnter(index)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
            style={{
                transition: "transform 150ms ease",
                transform: isDropTarget ? "translateY(10px)" : "none",
            }}
            className={nrDates === 1 ? metric.status || "unknown" : ""}
            color={nrDates === 1 ? metric.status || "unknown" : ""}
            details={
                <MetricDetails
                    changedFields={changedFields}
                    isFirstMetric={index === 0}
                    isLastMetric={index === lastIndex}
                    metricUuid={metricUuid}
                    reload={reload}
                    reportDate={reportDate}
                    reports={reports}
                    report={report}
                    settings={settings}
                    stopFilteringAndSorting={() => {
                        handleSort(null)
                        settings.hiddenTags.reset()
                        settings.metricsToHide.reset()
                    }}
                    subjectUuid={subjectUuid}
                />
            }
            expanded={settings.expandedItems.includes(metricUuid)}
            id={metricUuid}
            onExpand={() => settings.expandedItems.toggle(metricUuid)}
        >
            <TableCell>{metricName}</TableCell>
            {nrDates > 1 && (
                <MeasurementCells
                    dates={dates}
                    metric={metric}
                    metricUuid={metricUuid}
                    measurements={reversedMeasurements}
                    settings={settings}
                />
            )}
            {!columnsToHide.includes("trend") && (
                <TableCell sx={{ width: "150px" }}>
                    <TrendSparkline measurements={metric.recent_measurements} reportDate={reportDate} scale={scale} />
                </TableCell>
            )}
            {!columnsToHide.includes("status") && (
                <TableCell>
                    <Typography sx={{ paddingLeft: "6px", fontSize: "24px" }}>
                        <StatusIcon status={metric.status} statusStart={metric.status_start} />
                    </Typography>
                </TableCell>
            )}
            {!columnsToHide.includes("measurement") && (
                <TableCell align="right">
                    <MeasurementValue metric={metric} reportDate={reportDate} />
                </TableCell>
            )}
            {!columnsToHide.includes("target") && (
                <TableCell align="right">
                    <MeasurementTarget metric={metric} />
                </TableCell>
            )}
            {!columnsToHide.includes("unit") && <TableCell>{unit}</TableCell>}
            {!columnsToHide.includes("source") && (
                <TableCell>
                    <MeasurementSources metric={metric} />
                </TableCell>
            )}
            {!columnsToHide.includes("time_left") && (
                <TableCell>
                    <TimeLeft metric={metric} report={report} />
                </TableCell>
            )}
            {!columnsToHide.includes("overrun") && (
                <TableCell>
                    <Overrun
                        metric={metric}
                        metricUuid={metricUuid}
                        report={report}
                        measurements={measurements}
                        dates={dates}
                    />
                </TableCell>
            )}
            {!columnsToHide.includes("comment") && (
                <TableCell>
                    <DivWithHtml>{metric.comment}</DivWithHtml>
                </TableCell>
            )}
            {!columnsToHide.includes("issues") && (
                <TableCell>
                    <IssueStatus metric={metric} issueTrackerMissing={!report.issue_tracker} settings={settings} />
                </TableCell>
            )}
            {!columnsToHide.includes("tags") && (
                <TableCell>
                    {getMetricTags(metric).map((tag) => (
                        <Tag key={tag} tag={tag} />
                    ))}
                </TableCell>
            )}
            {!anyRowExpanded && (
                <ReadOnlyOrEditable
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    editableComponent={
                        <TableCell>
                            <DragHandleButton
                                ref={dragHandleRef}
                                label="Drag to reorder"
                                draggable
                                onDragStart={(e) => onDragStart(index, rowRef, e)}
                            />
                        </TableCell>
                    }
                />
            )}
            {anyRowExpanded && <TableCell />}
        </TableRowWithDetails>
    )
}
SubjectTableRow.propTypes = {
    changedFields: stringsPropType,
    columnsToHide: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    index: number,
    lastIndex: number,
    measurements: measurementsPropType,
    metricUuid: string,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: measurementsPropType,
    settings: settingsPropType,
    subjectUuid: string,
    onDragStart: func,
    onDragEnter: func,
    onDrop: func,
    isDropTarget: bool,
}
