import { useContext } from "react"
import { Icon, Message } from "semantic-ui-react"

import { DataModel } from "../context/DataModel"
import { Label, Popup } from "../semantic_ui_react_wrappers"
import { datePropType, metricPropType } from "../sharedPropTypes"
import { formatMetricValue, getMetricScale, getMetricValue, MILLISECONDS_PER_HOUR } from "../utils"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

export function MeasurementValue({ metric, reportDate }) {
    const dataModel = useContext(DataModel)
    const metricValue = getMetricValue(metric, dataModel)
    let value = metricValue || "?"
    const scale = getMetricScale(metric, dataModel)
    if (scale === "percentage") {
        value += "%"
    }
    value = formatMetricValue(scale, value)
    if (metric.latest_measurement) {
        const end = new Date(metric.latest_measurement.end)
        const now = reportDate ?? new Date()
        const staleMeasurementValue = now - end > MILLISECONDS_PER_HOUR // No new measurement for more than one hour means something is wrong
        let trigger
        if (staleMeasurementValue) {
            trigger = <Label color="red">{value}</Label>
        } else if (metric.latest_measurement.outdated) {
            trigger = (
                <Label color="yellow">
                    <Icon loading name="hourglass" /> {value}
                </Label>
            )
        } else {
            trigger = <span>{value}</span>
        }
        return (
            <Popup trigger={trigger} flowing hoverable>
                {staleMeasurementValue && (
                    <Message
                        negative
                        header="This metric was not recently measured"
                        content="This may indicate a problem with Quality-time itself. Please contact a system administrator."
                    />
                )}
                {metric.latest_measurement.outdated && (
                    <Message
                        warning
                        header="Latest measurement out of date"
                        content="The source configuration of this metric was changed after the latest measurement."
                    />
                )}
                <TimeAgoWithDate date={metric.latest_measurement.end}>
                    {metric.status ? "The metric was last measured" : "Last measurement attempt"}
                </TimeAgoWithDate>
                <br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>
                    {metric.status ? "The current value was first measured" : "The value is unknown since"}
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
