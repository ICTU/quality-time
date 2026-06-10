import { metricPropType, reportPropType } from "../sharedPropTypes"
import { SourceStatus } from "./SourceStatus"

export function MeasurementSources({ metric, report }) {
    const sources = metric.latest_measurement?.sources ?? []
    return sources.map((source, index) => [
        index > 0 && ", ",
        <SourceStatus key={source.source_uuid} metric={metric} measurementSource={source} report={report} />,
    ])
}
MeasurementSources.propTypes = {
    metric: metricPropType,
    report: reportPropType,
}
