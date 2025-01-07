import { SourceStatus } from "./SourceStatus"

export function MeasurementSources({ metric }) {
    const sources = metric.latest_measurement?.sources ?? []
    return sources.map((source) => [
        <SourceStatus key={source.source_uuid} metric={metric} measurement_source={source} />,
    ])
}
