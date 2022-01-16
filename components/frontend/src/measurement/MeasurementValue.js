import { useContext } from "react";
import { Popup } from "semantic-ui-react";
import { DataModel } from "../context/DataModel";
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { formatMetricScaleAndUnit, format_minutes, get_metric_value } from '../utils';

export function MeasurementValue({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricUnit = formatMetricScaleAndUnit(metricType, metric);
    const metricValue = get_metric_value(metric)
    const value = metricValue && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metricValue) : metricValue || "?";
    const valueText = <span>{value + metricUnit}</span>
    if (metric.latest_measurement) {
        return (
            <Popup trigger={valueText} flowing hoverable>
                <TimeAgoWithDate date={metric.latest_measurement.end}>{metric.status ? "Metric was last measured":"Last measurement attempt"}</TimeAgoWithDate><br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>{metric.status ? "Value was first measured":"Value unknown since"}</TimeAgoWithDate>
            </Popup>
        )
    }
    return valueText;
}
