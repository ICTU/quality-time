export function metricStatusOnDate(metric_uuid, metric, measurements, isoDateString) {
    const measurement = measurements?.find((m) => {
        return m.metric_uuid === metric_uuid && m.start.split("T")[0] <= isoDateString && isoDateString <= m.end.split("T")[0]
    });
    return measurement?.[metric.scale]?.status ?? "unknown";
}
