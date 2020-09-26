import React from 'react';
import { Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { SourceStatus } from './SourceStatus';
import { TrendSparkline } from './TrendSparkline';
import { MeasurementDetails } from './MeasurementDetails';
import { StatusIcon } from './StatusIcon';
import { Tag } from '../widgets/Tag';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { get_metric_name, get_metric_target, format_minutes } from '../utils';
import "./Measurement.css";

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
    const metric_direction = { "<": "≦", ">": "≧" }[metric.direction || metric_type.direction];
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
  function get_metric_unit() {
    const metric_unit_prefix = metric.scale === "percentage" ? "% " : " ";
    const metric_type_unit = metric_type.unit === 'minutes' && metric.scale !== 'percentage' ? 'hours' : metric_type.unit;
    return `${metric_unit_prefix}${metric.unit || metric_type_unit}`;
  }
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_type = props.datamodel.metrics[metric.type];
  const latest_measurements = metric.recent_measurements;
  const latest_measurement = latest_measurements.length > 0 ? latest_measurements[latest_measurements.length - 1] : null;
  const sources = (latest_measurement && latest_measurement.sources) || [];
  const metric_unit = get_metric_unit();
  const metric_name = get_metric_name(metric, props.datamodel);
  const details = <MeasurementDetails measurement={latest_measurement} metric_name={metric_name} scale={metric.scale} unit={metric_unit} {...props} />
  return (
    <TableRowWithDetails id={props.metric_uuid} className={metric.status} details={details}>
      <Table.Cell>{metric_name}</Table.Cell>
      {!props.hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={latest_measurements} scale={metric.scale} /></Table.Cell>}
      {!props.hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} /></Table.Cell>}
      {!props.hiddenColumns.includes("measurement") && <Table.Cell><MeasurementValue /></Table.Cell>}
      {!props.hiddenColumns.includes("target") && <Table.Cell>{measurement_target()}</Table.Cell>}
      {!props.hiddenColumns.includes("source") && <Table.Cell>{measurement_sources()}</Table.Cell>}
      {!props.hiddenColumns.includes("comment") && <Table.Cell><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
      {!props.hiddenColumns.includes("tags") && <Table.Cell>{metric.tags.sort().map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
    </TableRowWithDetails>
  )
}
