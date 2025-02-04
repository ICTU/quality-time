import { func, string } from "prop-types"
import { useContext } from "react"

import { set_metric_attribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { metricPropType, targetType } from "../sharedPropTypes"
import { formatMetricDirection, formatMetricScaleAndUnit, formatMetricValue, getMetricScale } from "../utils"

export function Target({ metric, metric_uuid, reload, target_type }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const metricScale = getMetricScale(metric, dataModel)
    const metricDirection = formatMetricDirection(metric, dataModel)
    const targetValue = metric[target_type]
    const unit = formatMetricScaleAndUnit(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type]
    const defaultTarget = metricType[target_type]
    const targetType = { debt_target: "technical debt target", near_target: "near target", target: "target" }[
        target_type
    ]
    let helperText =
        defaultTarget === metric[target_type] || defaultTarget === undefined
            ? ""
            : `Default ${targetType}: ${formatMetricValue(scale, defaultTarget)} ${unit}`
    if (target_type === "debt_target") {
        helperText = "Accept technical debt if the metric value is equal to or better than the technical debt target."
    }
    if (metricScale === "version_number") {
        return (
            <TextField
                disabled={disabled}
                label={`Metric ${targetType}`}
                startAdornment={metricDirection}
                onChange={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                value={targetValue}
            />
        )
    } else {
        const max = metricScale === "percentage" ? 100 : null
        return (
            <TextField
                disabled={disabled}
                endAdornment={unit}
                helperText={helperText}
                label={`Metric ${targetType}`}
                max={max}
                onChange={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                startAdornment={metricDirection}
                type="number"
                value={targetValue}
            />
        )
    }
}
Target.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    target_type: targetType,
}
