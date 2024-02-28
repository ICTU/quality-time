import { useContext } from 'react';
import PropTypes from 'prop-types';
import { Label, Table } from '../semantic_ui_react_wrappers';
import { DataModel } from "../context/DataModel";
import { DarkMode } from "../context/DarkMode";
import { IssueStatus } from '../issue/IssueStatus';
import { MetricDetails } from '../metric/MetricDetails';
import { MeasurementSources } from '../measurement/MeasurementSources';
import { MeasurementTarget } from '../measurement/MeasurementTarget';
import { MeasurementValue } from '../measurement/MeasurementValue';
import { StatusIcon } from '../measurement/StatusIcon';
import { Overrun } from '../measurement/Overrun';
import { TimeLeft } from '../measurement/TimeLeft';
import { TrendSparkline } from '../measurement/TrendSparkline';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import { formatMetricScale, get_metric_name, getMetricDirection, getMetricScale, getMetricTags, getMetricUnit } from '../utils';
import {
    datesPropType,
    metricPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    scalePropType,
    stringsPropType,
} from '../sharedPropTypes';

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
    dateOrderAscending: PropTypes.bool,
    metricValue: PropTypes.string,
    previousValue: PropTypes.string,
    scale: scalePropType,
}

function didValueImprove(didValueIncrease, direction) {
    return (didValueIncrease && direction === ">") || (!didValueIncrease && direction === "<")
}
didValueImprove.propTypes = {
    didValueIncrease: PropTypes.bool,
    direction: PropTypes.oneOf(["<", ">"]),
}

function DeltaCell({ dateOrderAscending, index, metric, metricValue, previousValue, status }) {
    const dataModel = useContext(DataModel);
    let label = null;
    if (index > 0 && previousValue !== "?" && metricValue !== "?" && previousValue !== metricValue) {
        // Note that the delta cell only gets content if the previous and current values are both available and unequal
        const scale = getMetricScale(metric, dataModel)
        const increased = didValueIncrease(dateOrderAscending, metricValue, previousValue, scale)
        const direction = getMetricDirection(metric, dataModel)
        const improved = didValueImprove(increased, direction)
        const evaluateTarget = metric.evaluate_targets ?? true
        let alt = "The measurement value changed";
        let color = "blue";
        if (evaluateTarget && improved) {
            alt = "The measurement value improved";
            color = "green"
        }
        if (evaluateTarget && !improved) {
            alt = "The measurement value worsened";
            color = "red"
        }
        let delta = increased ? "+" : "-"
        if (getMetricScale(metric) !== "version_number") {
            delta += `${Math.abs(metricValue - previousValue)}`
            alt += ` by ${delta}`
        }
        label = <Label aria-label={alt} basic color={color}>{delta}</Label>
    }
    return (
        <Table.Cell className={status} singleLine textAlign="right">
            {label}
        </Table.Cell>
    )
}
DeltaCell.propTypes = {
    dateOrderAscending: PropTypes.bool,
    metric: metricPropType,
    index: PropTypes.number,
    metricValue: PropTypes.string,
    previousValue: PropTypes.string,
    status: PropTypes.string,
}

function MeasurementCells({ dates, metric, metric_uuid, measurements, settings }) {
    const dataModel = useContext(DataModel)
    const showDeltaColumns = !settings.hiddenColumns.includes("delta")
    const dateOrderAscending = settings.dateOrder.value === "ascending"
    const scale = getMetricScale(metric, dataModel)
    const cells = []
    let previousValue = "?";
    dates.forEach((date, index) => {
        const isoDateString = date.toISOString().split("T")[0];
        const measurement = measurements?.find((m) => { return m.metric_uuid === metric_uuid && m.start.split("T")[0] <= isoDateString && isoDateString <= m.end.split("T")[0] })
        let metricValue = measurement?.[scale]?.value ?? "?";
        const status = measurement?.[scale]?.status ?? "unknown";
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
                />
            )
        }
        cells.push(<Table.Cell className={status} key={date} textAlign="right">{metricValue}{formatMetricScale(metric)}</Table.Cell>)
        previousValue = metricValue === "?" ? previousValue : metricValue;
    })
    return cells
}
MeasurementCells.propTypes = {
    dates: datesPropType,
    measurements: PropTypes.array,
    metric_uuid: PropTypes.string,
    metric: metricPropType,
    settings: settingsPropType,
}

function expandOrCollapseItem(expand, metric_uuid, expandedItems) {
    if (expand) {
        expandedItems.toggle(`${metric_uuid}:0`)
    } else {
        const items = expandedItems.value.filter((each) => each?.startsWith(metric_uuid));
        expandedItems.toggle(items[0])
    }
}

export function SubjectTableRow(
    {
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
        subject_uuid
    }
) {
    const dataModel = useContext(DataModel);
    const darkMode = useContext(DarkMode)
    const metricName = get_metric_name(metric, dataModel);
    const scale = getMetricScale(metric, dataModel)
    const unit = getMetricUnit(metric, dataModel);
    const nrDates = dates.length;
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
            {nrDates > 1 && <MeasurementCells dates={dates} metric={metric} metric_uuid={metric_uuid} measurements={reversedMeasurements} settings={settings} />}
            {nrDates === 1 && !settings.hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={metric.recent_measurements} report_date={reportDate} scale={scale} /></Table.Cell>}
            {nrDates === 1 && !settings.hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
            {nrDates === 1 && !settings.hiddenColumns.includes("measurement") && <Table.Cell textAlign="right"><MeasurementValue metric={metric} reportDate={reportDate} /></Table.Cell>}
            {nrDates === 1 && !settings.hiddenColumns.includes("target") && <Table.Cell textAlign="right"><MeasurementTarget metric={metric} /></Table.Cell>}
            {!settings.hiddenColumns.includes("unit") && <Table.Cell style={style}>{unit}</Table.Cell>}
            {!settings.hiddenColumns.includes("source") && <Table.Cell style={style}><MeasurementSources metric={metric} /></Table.Cell>}
            {!settings.hiddenColumns.includes("time_left") && <Table.Cell style={style}><TimeLeft metric={metric} report={report} /></Table.Cell>}
            {nrDates > 1 && !settings.hiddenColumns.includes("overrun") && <Table.Cell style={style}><Overrun metric={metric} metric_uuid={metric_uuid} report={report} measurements={measurements} dates={dates} /></Table.Cell>}
            {!settings.hiddenColumns.includes("comment") && <Table.Cell style={style}><div style={{ wordBreak: "break-word" }} dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
            {!settings.hiddenColumns.includes("issues") && <Table.Cell style={style}>
                <IssueStatus metric={metric} issueTrackerMissing={!report.issue_tracker} settings={settings} />
            </Table.Cell>}
            {!settings.hiddenColumns.includes("tags") && <Table.Cell style={style}>{getMetricTags(metric).map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
        </TableRowWithDetails>
    )
}
SubjectTableRow.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    index: PropTypes.number,
    lastIndex: PropTypes.number,
    measurements: PropTypes.array,
    metric_uuid: PropTypes.string,
    metric: metricPropType,
    reload: PropTypes.func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: PropTypes.array,
    settings: settingsPropType,
    subject_uuid: PropTypes.string,
}
