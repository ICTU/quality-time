import { Popup } from "../semantic_ui_react_wrappers";
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { get_metric_value } from '../utils';

export function MeasurementValue({ metric }) {
    const metricValue = get_metric_value(metric)
    let value = metricValue || "?";
    if (metric.scale === "percentage") { value += "%" }
    if (metric.latest_measurement) {
        return (
            <Popup trigger={<span>{value}</span>} flowing hoverable>
                <TimeAgoWithDate date={metric.latest_measurement.end}>{metric.status ? "The metric was last measured" : "Last measurement attempt"}</TimeAgoWithDate><br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>{metric.status ? "The current value was first measured" : "The value is unknown since"}</TimeAgoWithDate>
            </Popup>
        )
    }
    return <span>{value}</span>;
}
