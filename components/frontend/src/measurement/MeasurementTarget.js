import { useContext } from "react";
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { DataModel } from "../context/DataModel";
import { formatMetricDirection, formatMetricScale, formatMetricScaleAndUnit, get_metric_target } from '../utils';

export function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    if (metric?.evaluate_targets === false) { return null }
    const metricDirection = formatMetricDirection(metric, dataModel)
    const target = `${metricDirection} ${get_metric_target(metric)}${formatMetricScale(metric)}`
    if (metric.accept_debt) {
        const trigger = <Label color="grey">{target}</Label>
        const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric)
        let debtEnd = "";
        if (metric.debt_end_date) {
            const endDate = new Date(metric.debt_end_date);
            debtEnd = ` until ${endDate.toLocaleDateString()}`;
        }
        const allIssuesDone = metric.issue_status?.length > 0 ? metric.issue_status.every((status) => status.status_category === "done") : false
        let popupText = `Measurements ${metricDirection} ${metric.debt_target ?? 0}${unit} are accepted as technical debt${debtEnd}`
        if (allIssuesDone) {
            popupText += " but this technical debt target is no longer applied because all issues have been done."
        } else {
            popupText += "."
        }
        return (
            <Popup
                flowing
                hoverable
                on={['hover', 'focus']}
                trigger={trigger}
            >
                {popupText}
            </Popup>
        )
    }
    return target
}
