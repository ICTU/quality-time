import { getMetricScale } from "../utils";

export function metricStatusOnDate(metric_uuid, metric, measurements, date, dataModel) {
    const isoDateString = date.toISOString().split("T")[0];
    const measurement = measurements?.find((m) => {
        return m.metric_uuid === metric_uuid && m.start.split("T")[0] <= isoDateString && isoDateString <= m.end.split("T")[0]
    });
    const scale = getMetricScale(metric, dataModel)
    return measurement?.[scale]?.status ?? "unknown";
}
