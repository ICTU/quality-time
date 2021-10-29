import React, { useContext } from 'react';
import { Popup, Table } from 'semantic-ui-react';
import { formatMetricScaleAndUnit, format_minutes, get_metric_direction, get_metric_name, get_metric_tags, get_metric_target } from '../utils';
import { DataModel } from '../context/DataModel';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { IssueStatus } from './IssueStatus';
import { MetricDetails } from './MetricDetails';
import { SourceStatus } from './SourceStatus';
import { StatusIcon } from './StatusIcon';
import { TrendSparkline } from './TrendSparkline';
import "./Metric.css";

function MeasurementValue({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricUnit = formatMetricScaleAndUnit(metricType, metric);
    const value = metric.value && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metric.value) : metric.value || "?";
    const valueText = <span>{value + metricUnit}</span>
    if (metric.latest_measurement) {
        return (
            <Popup trigger={valueText} flowing hoverable>
                <TimeAgoWithDate date={metric.latest_measurement.end}>Last measured</TimeAgoWithDate><br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>First measured</TimeAgoWithDate>
            </Popup>
        )
    }
    return valueText;
}

function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricUnit = formatMetricScaleAndUnit(metricType, metric);
    const metric_direction = get_metric_direction(metric, dataModel)
    let debt_end = "";
    if (metric.debt_end_date) {
        const end_date = new Date(metric.debt_end_date);
        debt_end = ` until ${end_date.toLocaleDateString()}`;
    }
    const debt = metric.accept_debt ? ` (debt accepted${debt_end})` : "";
    let target = get_metric_target(metric);
    if (target && metricType.unit === "minutes" && metric.scale !== "percentage") {
        target = format_minutes(target)
    }
    return `${metric_direction} ${target}${metricUnit}${debt}`
}

function MeasurementSources({ metric }) {
    const sources = metric.latest_measurement?.sources ?? [];
    return sources.map(
        (source, index) => [index > 0 && ", ", <SourceStatus key={source.source_uuid} metric={metric} measurement_source={source} />]
    );
}

export function Metric({
    report,
    reports,
    report_date,
    subject_uuid,
    metric,
    metric_uuid,
    first_metric,
    last_metric,
    stop_sort,
    changed_fields,
    visibleDetailsTabs,
    toggleVisibleDetailsTab,
    hiddenColumns,
    reload
}) {
    const dataModel = useContext(DataModel);
    const metricType = dataModel.metrics[metric.type];
    const metricName = get_metric_name(metric, dataModel);
    const details = (
        <MetricDetails
            unit={formatMetricScaleAndUnit(metricType, metric, false)}
            report_date={report_date}
            reports={reports}
            report={report}
            subject_uuid={subject_uuid}
            metric_uuid={metric_uuid}
            first_metric={first_metric}
            last_metric={last_metric}
            stop_sort={stop_sort}
            changed_fields={changed_fields}
            visibleDetailsTabs={visibleDetailsTabs}
            toggleVisibleDetailsTab={toggleVisibleDetailsTab}
            reload={reload} />
    )
    const expanded = visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid)).length > 0;
    function onExpand(expand) {
        if (expand) {
            toggleVisibleDetailsTab(`${metric_uuid}:0`)
        } else {
            const tabs = visibleDetailsTabs.filter((each) => each?.startsWith(metric_uuid));
            if (tabs.length > 0) {
                toggleVisibleDetailsTab(tabs[0])
            }
        }
    }
    return (
        <TableRowWithDetails id={metric_uuid} className={metric.status} details={details} expanded={expanded} onExpand={(state) => onExpand(state)}>
            <Table.Cell>{metricName}</Table.Cell>
            {!hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={metric.recent_measurements} report_date={report_date} scale={metric.scale} /></Table.Cell>}
            {!hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
            {!hiddenColumns.includes("measurement") && <Table.Cell><MeasurementValue metric={metric} /></Table.Cell>}
            {!hiddenColumns.includes("target") && <Table.Cell><MeasurementTarget metric={metric} /></Table.Cell>}
            {!hiddenColumns.includes("source") && <Table.Cell><MeasurementSources metric={metric} /></Table.Cell>}
            {!hiddenColumns.includes("comment") && <Table.Cell><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
            {!hiddenColumns.includes("issues") && <Table.Cell><IssueStatus metric={metric} issueTracker={report.issue_tracker} /></Table.Cell>}
            {!hiddenColumns.includes("tags") && <Table.Cell>{get_metric_tags(metric).map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
        </TableRowWithDetails>
    )
}
