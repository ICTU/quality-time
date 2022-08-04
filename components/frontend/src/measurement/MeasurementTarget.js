import { useContext } from "react";
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { DataModel } from "../context/DataModel";
import { formatMetricDirection, formatMetricScale, formatMetricScaleAndUnit, get_metric_target } from '../utils';

function popupText(metric, debtEndDateInThePast, allIssuesDone, dataModel) {
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric)
    const metricDirection = formatMetricDirection(metric, dataModel)
    let debtEndDateText = ""
    let endDate;
    if (metric.debt_end_date) {
        endDate = new Date(metric.debt_end_date);
        debtEndDateText = debtEndDateInThePast ? "" : ` until ${endDate.toLocaleDateString()}`
    }
    let text = `Measurements ${metricDirection} ${metric.debt_target ?? 0}${unit} are accepted as technical debt${debtEndDateText}.`
    if (allIssuesDone || debtEndDateInThePast) {
        text += " However, this technical debt target is not applied because"
    }
    if (allIssuesDone) {
        text += " all issues for this metric have been marked done"
    }
    if (debtEndDateInThePast) {
        if (allIssuesDone) {
            text += " and"
        }
        text += ` technical debt was accepted until ${endDate.toLocaleDateString()}`
    }
    return text + text.endsWith(".") ? "" : "."
}

export function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    if (metric?.evaluate_targets === false) { return null }
    const metricDirection = formatMetricDirection(metric, dataModel)
    const target = `${metricDirection} ${get_metric_target(metric)}${formatMetricScale(metric)}`
    const allIssuesDone = metric.issue_status?.length > 0 ? metric.issue_status.every((status) => status.status_category === "done") : false
    let debtEndDateInThePast = false
    if (metric.debt_end_date) {
        const endDate = new Date(metric.debt_end_date);
        const today = new Date();
        debtEndDateInThePast = endDate.toISOString().split("T")[0] < today.toISOString().split("T")[0];
    }
    const label = allIssuesDone || debtEndDateInThePast ? <Label color="grey">{target}</Label> : <span>{target}</span>
    if (metric.accept_debt) {
        return (
            <Popup hoverable on={['hover', 'focus']} trigger={label}>
                {popupText(metric, debtEndDateInThePast, allIssuesDone, dataModel)}
            </Popup>
        )
    }
    return target
}
