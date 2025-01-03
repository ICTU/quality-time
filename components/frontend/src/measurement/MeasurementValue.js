import "./MeasurementValue.css"

import { bool, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { Label, Message, Popup } from "../semantic_ui_react_wrappers"
import { datePropType, measurementPropType, metricPropType } from "../sharedPropTypes"
import { IGNORABLE_SOURCE_ENTITY_STATUSES, SOURCE_ENTITY_STATUS_NAME } from "../source/source_entity_status"
import {
    formatMetricValue,
    getMetricScale,
    getMetricUnit,
    getMetricValue,
    isMeasurementOutdated,
    isMeasurementRequested,
    isMeasurementStale,
    sum,
} from "../utils"
import { IgnoreIcon, LoadingIcon } from "../widgets/icons"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"
import { WarningMessage } from "../widgets/WarningMessage"

function measurementValueLabel(hasIgnoredEntities, stale, updating, value) {
    const measurementValue = hasIgnoredEntities ? (
        <>
            <IgnoreIcon /> {value}
        </>
    ) : (
        value
    )
    if (stale) {
        return <Label color="red">{measurementValue}</Label>
    }
    if (updating) {
        return (
            <Label color="yellow">
                <LoadingIcon />
                {measurementValue}
            </Label>
        )
    }
    return <span>{measurementValue}</span>
}
measurementValueLabel.propTypes = {
    hasIgnoredEntities: bool,
    updating: bool,
    stale: bool,
    value: string,
}

function ignoredEntitiesCount(measurement) {
    const count = Object.fromEntries(IGNORABLE_SOURCE_ENTITY_STATUSES.map((status) => [status, 0]))
    measurement?.sources?.forEach((source) => {
        Object.values(source.entity_user_data ?? {}).forEach((entity) => {
            if (Object.keys(count).includes(entity.status)) {
                count[entity.status]++
            }
        })
    })
    return count
}
ignoredEntitiesCount.propTypes = {
    measurement: measurementPropType,
}

function ignoredEntitiesMessage(measurement, unit) {
    const count = ignoredEntitiesCount(measurement)
    let summary = `The measurement value excludes ${sum(count)} ${unit}.`
    let details = ""
    Object.entries(count).forEach(([status, status_count]) => {
        if (status_count > 0) {
            details += `Marked as ${SOURCE_ENTITY_STATUS_NAME[status].toLowerCase()}: ${status_count}. `
        }
    })
    return (
        <p>
            {summary}
            <br />
            {details}
        </p>
    )
}
ignoredEntitiesMessage.propTypes = {
    measurement: measurementPropType,
    unit: string,
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
    const unit = getMetricUnit(metric, dataModel)
    const stale = isMeasurementStale(metric, reportDate)
    const outdated = isMeasurementOutdated(metric)
    const requested = isMeasurementRequested(metric)
    const hasIgnoredEntities = sum(ignoredEntitiesCount(metric.latest_measurement)) > 0
    return (
        <Popup
            trigger={measurementValueLabel(hasIgnoredEntities, stale, outdated || requested, value)}
            flowing
            hoverable
        >
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
            {hasIgnoredEntities && (
                <Message
                    info
                    header={
                        <span>
                            <IgnoreIcon /> {`Ignored ${unit}`}
                        </span>
                    }
                    content={ignoredEntitiesMessage(metric.latest_measurement, unit)}
                />
            )}
            {metric.latest_measurement && (
                <>
                    <TimeAgoWithDate date={metric.latest_measurement.end}>
                        {metric.status ? "The metric was last measured" : "Last measurement attempt"}
                    </TimeAgoWithDate>
                    <br />
                    <TimeAgoWithDate date={metric.latest_measurement.start}>
                        {metric.status ? "The current value was first measured" : "The value is unknown since"}
                    </TimeAgoWithDate>
                </>
            )}
        </Popup>
    )
}
MeasurementValue.propTypes = {
    metric: metricPropType,
    reportDate: datePropType,
}
