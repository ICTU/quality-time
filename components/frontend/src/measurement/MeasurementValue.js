import { useContext } from "react"
import { Message } from "semantic-ui-react"
import { Label, Popup } from "../semantic_ui_react_wrappers"
import { DataModel } from "../context/DataModel"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"
import { getMetricScale, getMetricValue, MILLISECONDS_PER_HOUR } from "../utils"
import { datePropType, metricPropType } from "../sharedPropTypes"

export function MeasurementValue({ metric, reportDate }) {
    const dataModel = useContext(DataModel)
    const metricValue = getMetricValue(metric, dataModel)
    let value = metricValue || "?"
    if (getMetricScale(metric, dataModel) === "percentage") {
        value += "%"
    }
    if (metric.latest_measurement) {
        const end = new Date(metric.latest_measurement.end)
        const now = reportDate ?? new Date()
        const staleMeasurementValue = now - end > MILLISECONDS_PER_HOUR // No new measurement for more than one hour means something is wrong
        const trigger = staleMeasurementValue ? (
            <Label color="red">{value}</Label>
        ) : (
            <span>{value}</span>
        )
        return (
            <Popup trigger={trigger} flowing hoverable>
                {staleMeasurementValue && (
                    <Message
                        negative
                        header="This metric was not recently measured"
                        content="This may indicate a problem with Quality-time itself. Please contact a system administrator."
                    />
                )}
                <TimeAgoWithDate date={metric.latest_measurement.end}>
                    {metric.status ? "The metric was last measured" : "Last measurement attempt"}
                </TimeAgoWithDate>
                <br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>
                    {metric.status
                        ? "The current value was first measured"
                        : "The value is unknown since"}
                </TimeAgoWithDate>
            </Popup>
        )
    }
    return <span>{value}</span>
}
MeasurementValue.propTypes = {
    metric: metricPropType,
    reportDate: datePropType,
}
