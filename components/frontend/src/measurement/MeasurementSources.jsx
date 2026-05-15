import { Fragment, useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { identifyingParameterValues } from "../utils"
import { SourceStatus } from "./SourceStatus"

export function MeasurementSources({ metric }) {
    const dataModel = useContext(DataModelContext)
    const sources = metric.latest_measurement?.sources ?? []
    const anyIdentifying = sources.some((measurementSource) => {
        const source = metric.sources[measurementSource.source_uuid]
        return source && identifyingParameterValues(source, dataModel.sources?.[source.type]).length > 0
    })
    const sep = anyIdentifying ? <span style={{ display: "inline-block", width: "1.5em" }} /> : ", "
    return sources.map((source, index) => (
        <Fragment key={source.source_uuid}>
            {index > 0 && sep}
            <SourceStatus metric={metric} measurementSource={source} />
        </Fragment>
    ))
}
