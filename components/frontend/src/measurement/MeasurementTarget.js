import { useContext } from "react";
import { DataModel } from "../context/DataModel";
import { format_minutes, formatMetricDirection, get_metric_target } from '../utils';

export function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metric_direction = formatMetricDirection(metric, dataModel)
    let debt_end = "";
    if (metric.debt_end_date) {
        const end_date = new Date(metric.debt_end_date);
        debt_end = ` until ${end_date.toLocaleDateString()}`;
    }
    const debt = metric.accept_debt ? ` (debt accepted${debt_end})` : "";
    let target = get_metric_target(metric);
    if (target && metricType.unit === "minutes" && metric.scale !== "percentage") {
        target = format_minutes(target)
    }
    return `${metric_direction} ${target}${metric.scale === "percentage" ? "%" : ""}${debt}`
}
