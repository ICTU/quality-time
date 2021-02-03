import { Table } from "semantic-ui-react";
import { formatMetricScale, formatMetricUnit, format_metric_direction } from "../utils";
import './TrendTable.css'


export function MeasurementsRow({metricType, metricName, metric, measurements, dates, showTargetRow}) {

  const unit = formatMetricUnit(metricType, metric)
  const targetCells = []
  const measurementCells = []

  dates.forEach((date, index) => {
    let measurement;
    if (index === 0) {
      if (measurements?.length > 0) {
        measurement = measurements.reduce((max, m) => m.start > max.start ? m : max)  // for the first cell, always take the most recent measurement
      }
    } else {
      measurement = measurements?.find((m) => { return m.start <= date.toISOString() && date.toISOString() <= m.end })
    }
    
    const metric_value = !measurement?.[metric.scale]?.value ? "?" : measurement[metric.scale].value;
    const status = !measurement?.[metric.scale]?.status ? "unknown" : measurement[metric.scale].status;
    measurementCells.push(<Table.Cell className={status} key={date} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>)

    if (showTargetRow) {
      const target = !measurement?.[metric.scale]?.target ? "?" : measurement?.[metric.scale]?.target;
      const direction = !measurement?.[metric.scale]?.direction ? "≤" : measurement?.[metric.scale]?.direction;
      targetCells.push(<Table.Cell key={date} textAlign="right">{format_metric_direction(direction)} {target}</Table.Cell>)
    }
  })

  const unitCell = <Table.Cell style={{ background: "#f9fafb"}}>{unit}</Table.Cell>

  return (
    <>
      <Table.Row>
        <Table.Cell style={{ background: "#f9fafb"}}>{showTargetRow ? "Measurement" : metricName}</Table.Cell>
        {measurementCells}
        {unitCell}
      </Table.Row>
      {showTargetRow ? 
        <Table.Row>
          <Table.Cell style={{ background: "#f9fafb"}}>Target</Table.Cell>
          {targetCells}
          {unitCell}
        </Table.Row> : undefined}
    </>
  )
}