import { Table } from "semantic-ui-react";
import { formatMetricScale, formatMetricUnit, format_metric_direction, format_minutes } from "../utils";
import './TrendTable.css'


export function MeasurementsRow({ metricType, metricName, metric, measurements, dates, showTargetRow }) {

  const unit = formatMetricUnit(metricType, metric)
  const targetCells = []
  const measurementCells = []
  // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
  measurements.sort((m1, m2) => m1.start < m2.start ? 1 : -1)

  dates.forEach((date) => {
    const iso_date_string = date.toISOString().split("T")[0];
    const measurement = measurements?.find((m) => { return m.start.split("T")[0] <= iso_date_string && iso_date_string <= m.end.split("T")[0] })
    let metric_value = !measurement?.[metric.scale]?.value ? "?" : measurement[metric.scale].value;
    metric_value = metric_value !== "?" && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metric_value) : metric_value;
    const status = !measurement?.[metric.scale]?.status ? "unknown" : measurement[metric.scale].status;
    measurementCells.push(<Table.Cell className={status} key={date} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>)

    if (showTargetRow) {
      const target = !measurement?.[metric.scale]?.target ? "?" : measurement?.[metric.scale]?.target;
      const direction = !measurement?.[metric.scale]?.direction ? "≤" : measurement?.[metric.scale]?.direction;
      targetCells.push(<Table.Cell key={date} textAlign="right">{format_metric_direction(direction)} {target}</Table.Cell>)
    }
  })

  const unitCell = <Table.Cell style={{ background: "#f9fafb" }}>{unit}</Table.Cell>

  return (
    <>
      <Table.Row>
        <Table.Cell style={{ background: "#f9fafb" }}>{showTargetRow ? "Measurement" : metricName}</Table.Cell>
        {measurementCells}
        {unitCell}
      </Table.Row>
      {showTargetRow ?
        <Table.Row>
          <Table.Cell style={{ background: "#f9fafb" }}>Target</Table.Cell>
          {targetCells}
          {unitCell}
        </Table.Row> : undefined}
    </>
  )
}