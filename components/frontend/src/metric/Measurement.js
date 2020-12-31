import React from 'react';
import TimeAgo from 'react-timeago';
import { Popup, Table } from 'semantic-ui-react';
import { formatMetricScaleAndUnit, format_minutes, get_metric_direction, get_metric_name, get_metric_target } from '../utils';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import "./Measurement.css";
import { MeasurementDetails } from './MeasurementDetails';
import { SourceStatus } from './SourceStatus';
import { StatusIcon } from './StatusIcon';
import { TrendSparkline } from './TrendSparkline';

export function Measurement(props) {
  function MeasurementValue() {
    const value = metric.value && metric_type.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metric.value) : metric.value || "?";
    const now = new Date();
    const measurement_timestring = (latest_measurement && latest_measurement.end) || now.toISOString();
    const start = (latest_measurement && new Date(latest_measurement.start)) || now;
    const end = (latest_measurement && new Date(latest_measurement.end)) || now;
    return (
      <Popup
        trigger={<span>{value + metric_unit}</span>}
        flowing hoverable>
        Measured <TimeAgo date={measurement_timestring} /> ({start.toLocaleString()} - {end.toLocaleString()})
      </Popup>
    )
  }
  function measurement_target() {
    const metric_direction = get_metric_direction(metric, props.datamodel)
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
  function measurement_sources() {
    return sources.map((source, index) => [index > 0 && ", ", <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
      metric={metric} source={source} datamodel={props.datamodel} />])
  }
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_type = props.datamodel.metrics[metric.type];
  const latest_measurements = metric.recent_measurements;
  const latest_measurement = latest_measurements.length > 0 ? latest_measurements[latest_measurements.length - 1] : null;
  const sources = (latest_measurement && latest_measurement.sources) || [];
  const metric_unit = formatMetricScaleAndUnit(metric_type, metric);
  const metric_name = get_metric_name(metric, props.datamodel);
  const details = <MeasurementDetails measurement={latest_measurement} metric_name={metric_name} scale={metric.scale} unit={formatMetricScaleAndUnit(metric_type, metric, false)} {...props} />
  const expanded = props.visibleDetailsTabs.filter((tab) => tab.startsWith(props.metric_uuid)).length > 0;
  function onExpand(expand) {
    if (expand) {
      props.toggleVisibleDetailsTab(`${props.metric_uuid}:0`)
    } else {
      const tabs = props.visibleDetailsTabs.filter((each) => each.startsWith(props.metric_uuid));
      if (tabs.length > 0) {
        props.toggleVisibleDetailsTab(tabs[0])
      }
    }
  }
  return (
    <TableRowWithDetails id={props.metric_uuid} className={metric.status} details={details} expanded={expanded} onExpand={(state) => onExpand(state)}>
      <Table.Cell>{metric_name}</Table.Cell>
      {!props.hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={latest_measurements} report_date={props.report_date} scale={metric.scale} /></Table.Cell>}
      {!props.hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
      {!props.hiddenColumns.includes("measurement") && <Table.Cell><MeasurementValue /></Table.Cell>}
      {!props.hiddenColumns.includes("target") && <Table.Cell>{measurement_target()}</Table.Cell>}
      {!props.hiddenColumns.includes("source") && <Table.Cell>{measurement_sources()}</Table.Cell>}
      {!props.hiddenColumns.includes("comment") && <Table.Cell><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
      {!props.hiddenColumns.includes("tags") && <Table.Cell>{metric.tags.sort().map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
    </TableRowWithDetails>
  )
}
