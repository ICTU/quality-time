import { Message } from 'semantic-ui-react';
import { Label, Popup } from "../semantic_ui_react_wrappers";
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { get_metric_value } from '../utils';

export function MeasurementValue({ metric }) {
    const metricValue = get_metric_value(metric)
    let value = metricValue || "?";
    if (metric.scale === "percentage") { value += "%" }
    if (metric.latest_measurement) {
        const end = new Date(metric.latest_measurement.end)
        const now = new Date()
        const staleMeasurementValue = now - end > 1000 * 3600  // No new measurement for more than one hour means something is wrong
        const trigger = staleMeasurementValue ? <Label color="red">{value}</Label> : <span>{value}</span>;
        return (
            <Popup trigger={trigger} flowing hoverable>
                {staleMeasurementValue && (
                    <Message
                        negative
                        header="This metric was not recently measured"
                        content="This may indicate a problem with Quality-time itself. Please contact a system administrator."
                    />
                )}
                <TimeAgoWithDate date={metric.latest_measurement.end}>{metric.status ? "The metric was last measured" : "Last measurement attempt"}</TimeAgoWithDate><br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>{metric.status ? "The current value was first measured" : "The value is unknown since"}</TimeAgoWithDate>
            </Popup>
        )
    }
    return <span>{value}</span>;
}
