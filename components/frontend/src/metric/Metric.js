import React, { useEffect, useState } from 'react';
import { Measurement } from './Measurement';
import { get_measurements } from '../api/measurement';

export function Metric(props) {
  function fetch_measurement() {
    const report_date = props.report_date || new Date(3000, 1, 1);
    get_measurements(props.metric_uuid, report_date)
      .then(function (json) {
        setMeasurements(json.measurements);
        const last_measurement = json.measurements && json.measurements.length > 0 ? json.measurements[json.measurements.length - 1] : null;
        props.set_last_measurement(props.metric_uuid, last_measurement);
      })
  }
  const [measurements, setMeasurements] = useState([]);
  useEffect(() => { fetch_measurement() }, [props.nr_new_measurements, props.report_date]);
  const search = props.search_string;
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_name = metric.name || props.datamodel.metrics[metric.type].name;
  if (search && !metric_name.toLowerCase().includes(search.toLowerCase())) { return null }
  return (
    <Measurement
      datamodel={props.datamodel}
      measurements={measurements}
      metric_uuid={props.metric_uuid}
      nr_new_measurements={props.nr_new_measurements}
      reload={props.reload}
      fetch_measurement_and_reload={() => { fetch_measurement(); props.reload() }}
      report={props.report}
      readOnly={props.readOnly}
      subject_uuid={props.subject_uuid}
    />
  )
}
