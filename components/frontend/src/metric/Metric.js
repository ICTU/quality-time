import React, { useEffect, useState } from 'react';
import { Measurement } from './Measurement';
import { get_measurements } from '../api/measurement';

function last_measurement(measurements) {
  return measurements && measurements.length > 0 ? measurements[measurements.length - 1] : null;
}

function fetch_measurements(report_date, metric_uuid, setMeasurements, set_last_measurement) {
  const report_date_parameter = report_date || new Date(3000, 1, 1);
  get_measurements(metric_uuid, report_date_parameter)
    .then(function (json) {
      setMeasurements(json.measurements);
      set_last_measurement(metric_uuid, last_measurement(json.measurements));
    })
}

export function Metric(props) {
  const { report_date, metric_uuid, set_last_measurement, search_string } = props;
  const [measurements, setMeasurements] = useState([]);
  useEffect(() => {
    fetch_measurements(report_date, metric_uuid, setMeasurements, set_last_measurement)
    // eslint-disable-next-line
  }, [metric_uuid, props.nr_measurements, report_date]);
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_name = metric.name || props.datamodel.metrics[metric.type].name;
  if (search_string && !metric_name.toLowerCase().includes(search_string.toLowerCase())) { return null }
  return (
    <Measurement
      measurements={measurements}
      metric_uuid={metric_uuid}
      fetch_measurement_and_reload={() => {
        fetch_measurements(report_date, metric_uuid, setMeasurements, set_last_measurement);
        props.reload();
      }}
      {...props}
    />
  )
}
