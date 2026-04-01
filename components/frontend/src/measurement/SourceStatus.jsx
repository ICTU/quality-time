import { Tooltip, Typography } from "@mui/material"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { measurementSourcePropType, metricPropType } from "../sharedPropTypes"
import { getMetricName, getSourceName } from "../utils"
import { HyperLink } from "../widgets/HyperLink"
import { Label } from "../widgets/Label"

function hasMessage(measurementSource) {
    return measurementSource.connection_error || measurementSource.parse_error || measurementSource.info_message
}
hasMessage.propTypes = {
    measurementSource: measurementSourcePropType,
}

export function SourceStatus({ metric, measurementSource }) {
    const dataModel = useContext(DataModelContext)
    // Source may be deleted from report but still referenced in the latest measurement, be prepared:
    if (!Object.keys(metric.sources).includes(measurementSource.source_uuid)) {
        return null
    }
    const source = metric.sources[measurementSource.source_uuid]
    const sourceName = getSourceName(source, dataModel)
    const configError = !dataModel.metrics[metric.type].sources.includes(source.type)
    function sourceLabel() {
        return measurementSource.landing_url ? (
            <HyperLink url={measurementSource.landing_url}>{sourceName}</HyperLink>
        ) : (
            sourceName
        )
    }
    if (configError || hasMessage(measurementSource)) {
        let content
        let header
        let color = "error"
        if (configError) {
            content = `${sourceName} cannot be used to measure ${getMetricName(metric, dataModel)}.`
            header = "Configuration error"
        } else if (measurementSource.connection_error) {
            content = "Quality-time could not retrieve data from the source."
            header = "Connection error"
        } else if (measurementSource.parse_error) {
            content = "Quality-time could not parse the data received from the source."
            header = "Parse error"
        } else {
            content = measurementSource.info_message
            header = "Note"
            color = "informative"
        }
        return (
            <Tooltip
                title={
                    <>
                        <Typography>{header}</Typography>
                        {content}
                    </>
                }
            >
                <span>
                    <Label color={color}>{sourceLabel()}</Label>
                </span>
            </Tooltip>
        )
    } else {
        return sourceLabel()
    }
}
SourceStatus.propTypes = {
    metric: metricPropType,
    measurementSource: measurementSourcePropType,
}
