import { useContext } from "react";
import { Popup } from "../semantic_ui_react_wrappers/Popup";
import { DataModel } from "../context/DataModel";
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { format_minutes, get_metric_value } from '../utils';

export function MeasurementValue({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricValue = get_metric_value(metric)
    let value = metricValue && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metricValue) : metricValue || "?";
    if (metric.scale === "percentage") { value += "%"}
    if (metric.latest_measurement) {
        return (
            <Popup trigger={<span>{value}</span>} flowing hoverable>
                <TimeAgoWithDate date={metric.latest_measurement.end}>{metric.status ? "Metric was last measured":"Last measurement attempt"}</TimeAgoWithDate><br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>{metric.status ? "Value was first measured":"Value unknown since"}</TimeAgoWithDate>
            </Popup>
        )
    }
    return <span>{value}</span>;
}
