import { Tooltip, Typography } from "@mui/material"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { measurementSourcePropType, metricPropType } from "../sharedPropTypes"
import { getMetricName, getSourceName } from "../utils"
import { HyperLink } from "../widgets/HyperLink"
import { Label } from "../widgets/Label"

export function SourceStatus({ metric, measurement_source }) {
    const dataModel = useContext(DataModel)
    // Source may be deleted from report but still referenced in the latest measurement, be prepared:
    if (!Object.keys(metric.sources).includes(measurement_source.source_uuid)) {
        return null
    }
    const source = metric.sources[measurement_source.source_uuid]
    const source_name = getSourceName(source, dataModel)
    const configError = !dataModel.metrics[metric.type].sources.includes(source.type)
    function source_label() {
        return measurement_source.landing_url ? (
            <HyperLink url={measurement_source.landing_url}>{source_name}</HyperLink>
        ) : (
            source_name
        )
    }
    if (configError || measurement_source.connection_error || measurement_source.parse_error) {
        let content
        let header
        if (configError) {
            content = `${source_name} cannot be used to measure ${getMetricName(metric, dataModel)}.`
            header = "Configuration error"
        } else if (measurement_source.connection_error) {
            content = "Quality-time could not retrieve data from the source."
            header = "Connection error"
        } else {
            content = "Quality-time could not parse the data received from the source."
            header = "Parse error"
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
                    <Label color="error">{source_label()}</Label>
                </span>
            </Tooltip>
        )
    } else {
        return source_label()
    }
}
SourceStatus.propTypes = {
    metric: metricPropType,
    measurement_source: measurementSourcePropType,
}
