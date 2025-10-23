import { MenuItem, Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { setMetricAttribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { getSubjectTypeMetrics, referenceDocumentationURL } from "../utils"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"

export function metricTypeOption(key, metricType) {
    return {
        key: key,
        text: metricType.name,
        value: key,
        content: (
            <Stack direction="column" sx={{ whiteSpace: "normal" }}>
                {metricType.name}
                <Typography variant="body2">{metricType.description}</Typography>
            </Stack>
        ),
    }
}

export function metricTypeOptions(dataModel, subjectType) {
    // Return menu options for all metrics that support the subject type
    const metricTypeOptions = getSubjectTypeMetrics(subjectType, dataModel.subjects).map((key) =>
        metricTypeOption(key, dataModel.metrics[key]),
    )
    metricTypeOptions.sort((option1, option2) => option1.text > option2.text)
    return metricTypeOptions
}

export function allMetricTypeOptions(dataModel) {
    const metricTypeOptions = Object.keys(dataModel.metrics).map((key) => metricTypeOption(key, dataModel.metrics[key]))
    metricTypeOptions.sort((option1, option2) => option1.text > option2.text)
    return metricTypeOptions
}

export function usedMetricTypes(subject) {
    const metricTypes = new Set()
    for (const metric of Object.values(subject.metrics)) {
        metricTypes.add(metric.type)
    }
    return Array.from(metricTypes)
}

export function MetricType({ subjectType, metricType, metricUuid, reload }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const options = metricTypeOptions(dataModel, subjectType)
    const metricTypes = options.map((option) => option.key)
    if (!metricTypes.includes(metricType)) {
        options.push(metricTypeOption(metricType, dataModel.metrics[metricType]))
    }
    const hasExtraDocs = dataModel.metrics[metricType].documentation
    const howToConfigure = ` for ${hasExtraDocs ? "additional " : ""}information on how to configure this metric type.`
    return (
        <TextField
            disabled={disabled}
            helperText={
                <>
                    <ReadTheDocsLink url={referenceDocumentationURL(dataModel.metrics[metricType].name)} />
                    {howToConfigure}
                </>
            }
            label="Metric type"
            onChange={(value) => setMetricAttribute(metricUuid, "type", value, reload)}
            select
            value={metricType}
        >
            {options.map((option) => (
                <MenuItem key={option.key} value={option.value}>
                    {option.content}
                </MenuItem>
            ))}
        </TextField>
    )
}
MetricType.propTypes = {
    subjectType: string,
    metricType: string,
    metricUuid: string,
    reload: func,
}
