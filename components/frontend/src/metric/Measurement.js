import React from 'react';
import { Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { SourceStatus } from './SourceStatus';
import { TrendSparkline } from './TrendSparkline';
import { MeasurementDetails } from './MeasurementDetails';
import { StatusIcon } from './StatusIcon';
import { Tag } from '../widgets/Tag';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { get_metric_name, get_metric_target } from '../utils';
import "./Measurement.css";

function week_ago_iso_string() {
  let week_ago = new Date();
  week_ago.setDate(week_ago.getDate() - 7)
  return week_ago.toISOString();
}

export function Measurement(props) {
  function MeasurementValue() {
    const value = (latest_measurement && latest_measurement[metric_scale] && latest_measurement[metric_scale].value) || "?";
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
    return `${metric_direction} ${get_metric_target(metric)}${metric_unit} ${metric.accept_debt ? "(debt)" : ""}`
  }
  function measurement_sources() {
    return sources.map((source, index) => [index > 0 && ", ", <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
    metric={metric} source={source} datamodel={props.datamodel} />])
  }
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_type = props.datamodel.metrics[metric.type];
  const metric_scale = metric.scale || metric_type.default_scale || "count";
  const latest_measurement = props.measurements.length > 0 ? props.measurements[props.measurements.length - 1] : null;
  const latest_measurements = props.measurements.filter((measurement) => measurement.end >= week_ago_iso_string());
  const sources = (latest_measurement && latest_measurement.sources) || [];
  const metric_unit_prefix = metric_scale === "percentage" ? "% " : " ";
  const metric_unit = `${metric_unit_prefix}${metric.unit || metric_type.unit}`;
  const metric_name = get_metric_name(metric, props.datamodel);
  const details = <MeasurementDetails measurement={latest_measurement} metric_name={metric_name} scale={metric_scale} unit={metric_unit} {...props} />
  return (
    <TableRowWithDetails id={props.metric_uuid} className={metric.status} details={details}>
      <Table.Cell>{metric_name}</Table.Cell>
      <Table.Cell><TrendSparkline measurements={latest_measurements} scale={metric_scale} /></Table.Cell>
      <Table.Cell textAlign='center'><StatusIcon status={metric.status} /></Table.Cell>
      <Table.Cell><MeasurementValue /></Table.Cell>
      <Table.Cell>{measurement_target()}</Table.Cell>
      <Table.Cell>{measurement_sources()}</Table.Cell>
      <Table.Cell><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>
      <Table.Cell>{metric.tags.sort().map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>
    </TableRowWithDetails>
  )
}
