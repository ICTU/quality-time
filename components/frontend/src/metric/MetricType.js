import { Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { set_metric_attribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { getSubjectTypeMetrics } from "../utils"

export function metricTypeOption(key, metricType) {
    return {
        key: key,
        text: metricType.name,
        value: key,
        content: (
            <Stack direction="column">
                {metricType.name}
                <Typography variant="body2">{metricType.description}</Typography>
            </Stack>
        ),
    }
}

export function metricTypeOptions(dataModel, subjectType) {
    // Return menu options for all metric that support the subject type
    return getSubjectTypeMetrics(subjectType, dataModel.subjects).map((key) =>
        metricTypeOption(key, dataModel.metrics[key]),
    )
}

export function allMetricTypeOptions(dataModel) {
    return Object.keys(dataModel.metrics).map((key) => metricTypeOption(key, dataModel.metrics[key]))
}

export function usedMetricTypes(subject) {
    const metricTypes = new Set()
    Object.values(subject.metrics).forEach((metric) => metricTypes.add(metric.type))
    return Array.from(metricTypes)
}

export function MetricType({ subjectType, metricType, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const options = metricTypeOptions(dataModel, subjectType)
    const metricTypes = options.map((option) => option.key)
    if (!metricTypes.includes(metricType)) {
        options.push(metricTypeOption(metricType, dataModel.metrics[metricType]))
    }
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Metric type"
            options={options}
            set_value={(value) => set_metric_attribute(metric_uuid, "type", value, reload)}
            value={metricType}
        />
    )
}
MetricType.propTypes = {
    subjectType: string,
    metricType: string,
    metric_uuid: string,
    reload: func,
}
