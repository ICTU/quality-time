import React from 'react';
import { Popup, Table } from 'semantic-ui-react';
import { formatMetricScaleAndUnit, format_minutes, get_metric_direction, get_metric_name, get_metric_tags, get_metric_target } from '../utils';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { IssueStatus } from './IssueStatus';
import { MetricDetails } from './MetricDetails';
import { SourceStatus } from './SourceStatus';
import { StatusIcon } from './StatusIcon';
import { TrendSparkline } from './TrendSparkline';
import "./Metric.css";

function MeasurementValue({ metric, metric_type, metric_unit, latest_measurement }) {
    const value = metric.value && metric_type.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metric.value) : metric.value || "?";
    const valueText = <span>{value + metric_unit}</span>
    if (latest_measurement) {
        return (
            <Popup trigger={valueText} flowing hoverable>
                <TimeAgoWithDate date={latest_measurement.end}>Last measured</TimeAgoWithDate><br />
                <TimeAgoWithDate date={latest_measurement.start}>First measured</TimeAgoWithDate>
            </Popup>
        )
    }
    return valueText;
}

function MeasurementTarget({ datamodel, metric, metric_type, metric_unit }) {
    const metric_direction = get_metric_direction(metric, datamodel)
    let debt_end = "";
    if (metric.debt_end_date) {
        const end_date = new Date(metric.debt_end_date);
        debt_end = ` until ${end_date.toLocaleDateString()}`;
    }
    const debt = metric.accept_debt ? ` (debt accepted${debt_end})` : "";
    let target = get_metric_target(metric);
    if (target && metric_type.unit === "minutes" && metric.scale !== "percentage") {
        target = format_minutes(target)
    }
    return `${metric_direction} ${target}${metric_unit}${debt}`
}

function MeasurementSources({ datamodel, metric, latest_measurement }) {
    const sources = latest_measurement?.sources ?? [];
    return sources.map((source, index) => [index > 0 && ", ", <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
        metric={metric} source={source} datamodel={datamodel} />])
}

export function Metric({
    datamodel,
    reports_overview,
    report,
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
    const metric_type = datamodel.metrics[metric.type];
    const latest_measurements = metric.recent_measurements;
    const latest_measurement = latest_measurements.length > 0 ? latest_measurements[latest_measurements.length - 1] : null;
    const metric_unit = formatMetricScaleAndUnit(metric_type, metric);
    const metric_name = get_metric_name(metric, datamodel);
    const details = (
        <MetricDetails
            measurement={latest_measurement}
            metric_name={metric_name}
            scale={metric.scale}
            unit={formatMetricScaleAndUnit(metric_type, metric, false)}
            datamodel={datamodel}
            report_date={report_date}
            reports={reports_overview}
            report={report}
            subject_uuid={subject_uuid}
            metric_uuid={metric_uuid}
            metric_unit={metric_unit}
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
            <Table.Cell>{metric_name}</Table.Cell>
            {!hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={latest_measurements} report_date={report_date} scale={metric.scale} /></Table.Cell>}
            {!hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
            {!hiddenColumns.includes("measurement") && <Table.Cell><MeasurementValue metric={metric} metric_type={metric_type} metric_unit={metric_unit} latest_measurement={latest_measurement} /></Table.Cell>}
            {!hiddenColumns.includes("target") && <Table.Cell><MeasurementTarget datamodel={datamodel} metric={metric} metric_type={metric_type} metric_unit={metric_unit} /></Table.Cell>}
            {!hiddenColumns.includes("source") && <Table.Cell><MeasurementSources datamodel={datamodel} metric={metric} latest_measurement={latest_measurement} /></Table.Cell>}
            {!hiddenColumns.includes("comment") && <Table.Cell><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
            {!hiddenColumns.includes("issues") && <Table.Cell><IssueStatus metric={metric} /></Table.Cell>}
            {!hiddenColumns.includes("tags") && <Table.Cell>{get_metric_tags(metric).map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
        </TableRowWithDetails>
    )
}
