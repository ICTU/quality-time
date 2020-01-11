import React from 'react';
import { Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { SourceStatus } from './SourceStatus';
import { TrendSparkline } from './TrendSparkline';
import { MeasurementDetails } from './MeasurementDetails';
import { StatusIcon } from './StatusIcon';
import { Tag } from '../widgets/Tag';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { get_metric_name } from '../utils';

function week_ago_iso_string() {
  let week_ago = new Date();
  week_ago.setDate(week_ago.getDate() - 7)
  return week_ago.toISOString();
}

export function Measurement(props) {
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_type = props.datamodel.metrics[metric.type];
  const metric_scale = metric.scale || metric_type.default_scale || "count";
  var latest_measurement, start, end, value, status, sources, measurement_timestring;
  if (props.measurements.length === 0) {
    latest_measurement = null;
    value = "?";
    status = null;
    sources = [];
    start = new Date();
    end = new Date();
    measurement_timestring = end.toISOString();
  } else {
    latest_measurement = props.measurements[props.measurements.length - 1];
    sources = latest_measurement.sources;
    value = (latest_measurement[metric_scale] && latest_measurement[metric_scale].value) || "?";
    status = (latest_measurement[metric_scale] && latest_measurement[metric_scale].status) || null;
    start = new Date(latest_measurement.start);
    end = new Date(latest_measurement.end);
    measurement_timestring = latest_measurement.end;
  }
  const target = metric.accept_debt ? metric.debt_target || 0 : metric.target;
  const metric_direction = {"<": "≦", ">": "≧"}[metric.direction || metric_type.direction];
  const metric_unit_prefix = metric_scale === "percentage" ? "% " : " ";
  const metric_unit = `${metric_unit_prefix}${metric.unit || metric_type.unit}`;
  const metric_name = get_metric_name(metric, props.datamodel);
  const details = <MeasurementDetails
    measurement={latest_measurement}
    metric_name={metric_name}
    scale={metric_scale}
    unit={metric_unit}
    {...props}
  />
  return (
    <TableRowWithDetails id={props.metric_uuid} positive={status === "target_met"} negative={status === "target_not_met"} warning={status === "near_target_met"} active={status === "debt_target_met"} details={details}>
      <Table.Cell>
        {metric_name}
      </Table.Cell>
      <Table.Cell>
        <TrendSparkline measurements={props.measurements.filter((measurement) => measurement.end >= week_ago_iso_string())} scale={metric_scale} />
      </Table.Cell>
      <Table.Cell>
        <StatusIcon status={status} />
      </Table.Cell>
      <Table.Cell>
        <Popup
          trigger={<span>{value + metric_unit}</span>}
          flowing hoverable>
          Measured <TimeAgo date={measurement_timestring} /> ({start.toLocaleString()} - {end.toLocaleString()})
          </Popup>
      </Table.Cell>
      <Table.Cell>
        {metric_direction} {target}{metric_unit} {metric.accept_debt ? "(debt)" : ""}
      </Table.Cell>
      <Table.Cell>
        {sources.map((source, index) => [index > 0 && ", ", <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
          metric={metric} source={source} datamodel={props.datamodel} />])}
      </Table.Cell>
      <Table.Cell>
        <div dangerouslySetInnerHTML={{__html: metric.comment}}/>
      </Table.Cell>
      <Table.Cell>
        {metric.tags.sort().map((tag) => <Tag key={tag} tag={tag} />)}
      </Table.Cell>
    </TableRowWithDetails>
  )
}
