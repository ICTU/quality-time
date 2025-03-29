import { func, string } from "prop-types"
import { useContext } from "react"

import { setMetricAttribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { metricPropType, targetType } from "../sharedPropTypes"
import { formatMetricDirection, formatMetricScaleAndUnit, formatMetricValue, getMetricScale } from "../utils"

export function Target({ metric, metricUuid, reload, targetType }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const metricScale = getMetricScale(metric, dataModel)
    const metricDirection = formatMetricDirection(metric, dataModel)
    const targetValue = metric[targetType]
    const unit = formatMetricScaleAndUnit(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type]
    const defaultTarget = metricType[targetType]
    const targetTypeLabel = { debt_target: "technical debt target", near_target: "near target", target: "target" }[
        targetType
    ]
    let helperText =
        defaultTarget === metric[targetType] || defaultTarget === undefined
            ? ""
            : `Default ${targetTypeLabel}: ${formatMetricValue(scale, defaultTarget)} ${unit}`
    if (targetType === "debt_target") {
        helperText = "Accept technical debt if the metric value is equal to or better than the technical debt target."
    }
    if (metricScale === "version_number") {
        return (
            <TextField
                disabled={disabled}
                label={`Metric ${targetTypeLabel}`}
                startAdornment={metricDirection}
                onChange={(value) => setMetricAttribute(metricUuid, targetType, value, reload)}
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
                label={`Metric ${targetTypeLabel}`}
                max={max}
                onChange={(value) => setMetricAttribute(metricUuid, targetType, value, reload)}
                startAdornment={metricDirection}
                type="number"
                value={targetValue}
            />
        )
    }
}
Target.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    targetType: targetType,
}
