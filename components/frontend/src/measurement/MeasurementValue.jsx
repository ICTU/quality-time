import "./MeasurementValue.css"

import { Alert, Tooltip, Typography } from "@mui/material"
import { bool, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
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
    isSourceConfigurationComplete,
    sum,
} from "../utils"
import { IgnoreIcon, LoadingIcon } from "../widgets/icons"
import { Label } from "../widgets/Label"
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
        return (
            <span>
                <Label color="error">{measurementValue}</Label>
            </span>
        )
    }
    if (updating) {
        return (
            <span>
                <Label color="warning">
                    <LoadingIcon />
                    {measurementValue}
                </Label>
            </span>
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
    for (const source of measurement?.sources ?? []) {
        // Ignore entity user data that refers to entities that no longer exist by checking the entity keys
        const validKeys = (source.entities ?? []).map((entity) => entity.key)
        for (const [entityKey, entity] of Object.entries(source.entity_user_data ?? {})) {
            if (validKeys.includes(entityKey) && Object.keys(count).includes(entity.status)) {
                count[entity.status]++
            }
        }
    }
    return count
}
ignoredEntitiesCount.propTypes = {
    measurement: measurementPropType,
}

function ignoredEntitiesMessage(measurement, unit) {
    const count = ignoredEntitiesCount(measurement)
    let summary = `The measurement value excludes ${sum(count)} ${unit}.`
    let details = ""
    for (const [status, statusCount] of Object.entries(count)) {
        if (statusCount > 0) {
            details += `Marked as ${SOURCE_ENTITY_STATUS_NAME[status].toLowerCase()}: ${statusCount}. `
        }
    }
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
    const unit = getMetricUnit(metric, dataModel, value)
    const stale = isMeasurementStale(metric, reportDate)
    const complete = isSourceConfigurationComplete(dataModel, metric)
    const outdated = isMeasurementOutdated(metric)
    const requested = isMeasurementRequested(metric)
    const updating = complete && (outdated || requested)
    const hasIgnoredEntities = sum(ignoredEntitiesCount(metric.latest_measurement)) > 0
    return (
        <Tooltip
            slotProps={{ tooltip: { sx: { maxWidth: "32em" } } }}
            title={
                <div>
                    <WarningMessage showIf={stale} title="This metric was not recently measured">
                        This may indicate a problem with Quality-time itself. Please contact a system administrator.
                    </WarningMessage>
                    <WarningMessage showIf={!complete} title="Source configuration incomplete">
                        The source configuration of this metric is not complete. Add at least one source and make sure
                        all mandatory parameters for all sources have been provided.
                    </WarningMessage>
                    <WarningMessage showIf={outdated} title="Latest measurement out of date">
                        The source configuration of this metric was changed after the latest measurement.
                    </WarningMessage>
                    <WarningMessage showIf={requested} title="Measurement requested">
                        An update of the latest measurement was requested by a user.
                    </WarningMessage>
                    {hasIgnoredEntities && (
                        <Alert severity="info">
                            <Typography>
                                <IgnoreIcon /> {`Ignored ${unit}`}
                            </Typography>
                            {ignoredEntitiesMessage(metric.latest_measurement, unit)}
                        </Alert>
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
                </div>
            }
        >
            {measurementValueLabel(hasIgnoredEntities, stale, updating, value)}
        </Tooltip>
    )
}
MeasurementValue.propTypes = {
    metric: metricPropType,
    reportDate: datePropType,
}
