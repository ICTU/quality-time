import { useContext } from "react";
import { DataModel } from "../context/DataModel";
import { formatMetricDirection, get_metric_target } from '../utils';

export function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    const metricDirection = formatMetricDirection(metric, dataModel)
    let debtEnd = "";
    if (metric.debt_end_date) {
        const endDate = new Date(metric.debt_end_date);
        debtEnd = ` until ${endDate.toLocaleDateString()}`;
    }
    const debt = metric.accept_debt ? ` (debt accepted${debtEnd})` : "";
    const target = get_metric_target(metric);
    return `${metricDirection} ${target}${metric.scale === "percentage" ? "%" : ""}${debt}`
}
