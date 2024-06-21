import { bool, string } from "prop-types"
import { useContext } from "react"
import { Icon } from "semantic-ui-react"

import { DataModel } from "../context/DataModel"
import { Label, Popup } from "../semantic_ui_react_wrappers"
import { datePropType, metricPropType } from "../sharedPropTypes"
import {
    formatMetricValue,
    getMetricScale,
    getMetricValue,
    isMeasurementRequested,
    MILLISECONDS_PER_HOUR,
} from "../utils"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"
import { WarningMessage } from "../widgets/WarningMessage"

function measurementValueLabel(stale, updating, value) {
    if (stale) {
        return <Label color="red">{value}</Label>
    }
    if (updating) {
        return (
            <Label color="yellow">
                <Icon loading name="hourglass" /> {value}
            </Label>
        )
    }
    return <span>{value}</span>
}
measurementValueLabel.propTypes = {
    stale: bool,
    updating: bool,
    value: string,
}

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
        const stale = now - end > MILLISECONDS_PER_HOUR // No new measurement for more than one hour means something is wrong
        const outdated = metric.latest_measurement.outdated ?? false
        const requested = isMeasurementRequested(metric)
        return (
            <Popup trigger={measurementValueLabel(stale, outdated || requested, value)} flowing hoverable>
                <WarningMessage
                    showIf={stale}
                    header="This metric was not recently measured"
                    content="This may indicate a problem with Quality-time itself. Please contact a system administrator."
                />
                <WarningMessage
                    showIf={outdated}
                    header="Latest measurement out of date"
                    content="The source configuration of this metric was changed after the latest measurement."
                />
                <WarningMessage
                    showIf={requested}
                    header="Measurement requested"
                    content="An update of the latest measurement was requested by a user."
                />
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
