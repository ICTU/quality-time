import { useContext } from "react";
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { DataModel } from "../context/DataModel";
import { formatMetricDirection, formatMetricScale, formatMetricScaleAndUnit, get_metric_target } from '../utils';

function popupText(metric, dataModel) {
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric)
    const metricDirection = formatMetricDirection(metric, dataModel)
    let debtEndDateInThePast = false;
    let debtEndDateText = ""
    let endDate;
    if (metric.debt_end_date) {
        endDate = new Date(metric.debt_end_date);
        const today = new Date();
        debtEndDateInThePast = endDate.toISOString().split("T")[0] < today.toISOString().split("T")[0];
        debtEndDateText = debtEndDateInThePast ? "" : ` until ${endDate.toLocaleDateString()}`
    }
    const allIssuesDone = metric.issue_status?.length > 0 ? metric.issue_status.every((status) => status.status_category === "done") : false
    let popupText = `Measurements ${metricDirection} ${metric.debt_target ?? 0}${unit} are accepted as technical debt${debtEndDateText}.`
    if (allIssuesDone || debtEndDateInThePast) {
        popupText += " However, this technical debt target is not applied because"
    }
    if (allIssuesDone) {
        popupText += " all issues for this metric have been marked done"
    }
    if (debtEndDateInThePast) {
        if (allIssuesDone) {
            popupText += " and"
        }
        popupText += ` technical debt was accepted until ${endDate.toLocaleDateString()}`
    }
    popupText += "."
    return popupText
}

export function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    if (metric?.evaluate_targets === false) { return null }
    const metricDirection = formatMetricDirection(metric, dataModel)
    const target = `${metricDirection} ${get_metric_target(metric)}${formatMetricScale(metric)}`
    if (metric.accept_debt) {
        return (
            <Popup
                hoverable
                on={['hover', 'focus']}
                trigger={<Label color="grey">{target}</Label>}
            >
                {popupText(metric, dataModel)}
            </Popup>
        )
    }
    return target
}
