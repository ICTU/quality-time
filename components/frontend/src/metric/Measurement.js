import React from 'react';
import { Icon, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { SourceStatus } from './SourceStatus';
import { TrendSparkline } from './TrendSparkline';
import { MeasurementDetails } from './MeasurementDetails';
import { Tag } from '../widgets/Tag';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';

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
  const status_icon = {
    target_met: 'check', near_target_met: 'warning', debt_target_met: 'money',
    target_not_met: 'x', null: 'question'
  }[status];
  const target = metric.accept_debt ? metric.debt_target : metric.target;
  const metric_direction = {"<": "≦", ">": "≧"}[metric.direction || metric_type.direction];
  const positive = status === "target_met";
  const active = status === "debt_target_met";
  const negative = status === "target_not_met";
  const warning = status === "near_target_met";
  const metric_unit_prefix = metric_scale === "percentage" ? "% " : " ";
  const metric_unit = `${metric_unit_prefix}${metric.unit || metric_type.unit}`;
  const metric_name = metric.name || metric_type.name;
  let week_ago = new Date();
  week_ago.setDate(week_ago.getDate() - 7)
  const week_ago_string = week_ago.toISOString();
  const details = <MeasurementDetails
    datamodel={props.datamodel}
    fetch_measurement_and_reload={props.fetch_measurement_and_reload}
    first_metric={props.first_metric}
    last_metric={props.last_metric}
    measurement={latest_measurement}
    measurements={props.measurements}
    metric_name={metric_name}
    metric_uuid={props.metric_uuid}
    readOnly={props.readOnly}
    reload={props.reload}
    report={props.report}
    scale={metric_scale}
    stop_sort={props.stop_sort}
    subject_uuid={props.subject_uuid}
    unit={metric_unit}
    changed_fields={props.changed_fields}
  />
  return (
    <TableRowWithDetails id={props.metric_uuid} show_details={Object.keys(metric.sources || []).length === 0} positive={positive} negative={negative} warning={warning} active={active} details={details}>
      <Table.Cell>
        {metric_name}
      </Table.Cell>
      <Table.Cell>
        <TrendSparkline measurements={props.measurements.filter((measurement) => measurement.end >= week_ago_string)} scale={metric_scale} />
      </Table.Cell>
      <Table.Cell>
        <Icon size='large' name={status_icon} />
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
