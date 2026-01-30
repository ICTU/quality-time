import { Tooltip } from "@mui/material"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { metricPropType } from "../sharedPropTypes"
import {
    formatMetricDirection,
    formatMetricScale,
    formatMetricScaleAndUnit,
    formatMetricValue,
    getMetricScale,
    getMetricTarget,
    isValidISODate,
} from "../utils"
import { Label } from "../widgets/Label"

function popupText(metric, debtEndDateInThePast, allIssuesDone, dataModel) {
    const unit = formatMetricScaleAndUnit(metric, dataModel, metric.debt_target)
    const metricDirection = formatMetricDirection(metric, dataModel)
    let debtEndDateText = ""
    let endDate
    if (metric.debt_end_date && isValidISODate(metric.debt_end_date)) {
        endDate = new Date(metric.debt_end_date)
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
    return text + (text.endsWith(".") ? "" : ".")
}

export function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    if (metric?.evaluate_targets === false) {
        return null
    }
    const metricDirection = formatMetricDirection(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const target = `${metricDirection} ${formatMetricValue(scale, getMetricTarget(metric))}${formatMetricScale(metric, dataModel)}`
    if (!metric.accept_debt) {
        return <>{target}</>
    }
    const allIssuesDone =
        metric.issue_status?.length > 0
            ? metric.issue_status.every((status) => status.status_category === "done")
            : false
    let debtEndDateInThePast = false
    if (metric.debt_end_date && isValidISODate(metric.debt_end_date)) {
        const endDate = new Date(metric.debt_end_date)
        const today = new Date()
        debtEndDateInThePast = endDate.toISOString().split("T")[0] < today.toISOString().split("T")[0]
    }
    const label = allIssuesDone || debtEndDateInThePast ? <Label color="debt_target_met">{target}</Label> : target
    return (
        <Tooltip title={<span>{popupText(metric, debtEndDateInThePast, allIssuesDone, dataModel)}</span>}>
            <span>{label}</span>
        </Tooltip>
    )
}
MeasurementTarget.propTypes = {
    metric: metricPropType,
}
