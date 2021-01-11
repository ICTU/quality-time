import { Table } from "semantic-ui-react";
import { formatMetricScale, formatMetricUnit } from "../utils";


export function MeasurementsRow({metricType, metric, metricMeasurements, dates, preCells}) {

  const unit = formatMetricUnit(metricType, metric)
  
  const measurementCells = dates.map((date, index) => {
      let measurement;
      if (index === 0) {
        measurement = metricMeasurements?.[0]  // for the first cell, always take the first available measurement
      } else {
        measurement = metricMeasurements?.find((measurement) => {
          return measurement.start <= date.toISOString() && date.toISOString() <= measurement.end
        })
      }

      const metric_value = !measurement?.[metric.scale]?.value ? "?" : measurement[metric.scale].value;
      const status = !measurement?.[metric.scale]?.status ? "unknown" : measurement.[metric.scale].status;
      return <Table.Cell className={status} key={date} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>
    })

  return (
    <Table.Row>
      {preCells}
      {measurementCells}
      <Table.Cell><strong>{unit}</strong></Table.Cell>
    </Table.Row>
  )
}