import { Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { setMetricAttribute } from "../api/metric"
import { DataModelContext } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { metricPropType, reportPropType, subjectPropType } from "../sharedPropTypes"
import { getMetricTypeName, getSubjectTypeMetrics, referenceDocumentationURL } from "../utils"
import { ItemTypeSelector } from "../widgets/ItemTypeSelector"
import { ItemTypeSelectorTextField } from "../widgets/ItemTypeSelectorTextField"
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

export function usedMetricTypesInSubject(subject) {
    const metricTypes = new Set()
    for (const metric of Object.values(subject.metrics)) {
        metricTypes.add(metric.type)
    }
    return Array.from(metricTypes)
}

export function usedMetricTypesInReport(report) {
    const metricTypes = new Set()
    for (const subject of Object.values(report.subjects)) {
        usedMetricTypesInSubject(subject).forEach((metricType) => metricTypes.add(metricType))
    }
    return Array.from(metricTypes)
}

export function MetricTypeSelector({ metric, metricUuid, reload, report, subject }) {
    const dataModel = useContext(DataModelContext)
    const permissions = useContext(PermissionsContext)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const metricType = metric.type
    const hasExtraDocs = dataModel.metrics[metricType].documentation
    const howToConfigure = ` for ${hasExtraDocs ? "additional " : ""}information on how to configure this metric type.`
    return (
        <ItemTypeSelector
            allItemSubtypes={allMetricTypeOptions(dataModel)}
            itemSubtypes={metricTypeOptions(dataModel, subject.type)}
            itemType="metric"
            onClick={(value) => setMetricAttribute(metricUuid, "type", value, reload)}
            renderAnchor={(handleMenu) => (
                <ItemTypeSelectorTextField
                    disabled={disabled}
                    handleMenu={handleMenu}
                    helperText={
                        <>
                            <ReadTheDocsLink url={referenceDocumentationURL(getMetricTypeName(metric, dataModel))} />
                            {howToConfigure}
                        </>
                    }
                    label="Metric type"
                    value={getMetricTypeName(metric, dataModel)}
                />
            )}
            usedItemSubtypeKeysInReport={usedMetricTypesInReport(report)}
            usedItemSubtypeKeysInSubject={usedMetricTypesInSubject(subject)}
        />
    )
}
MetricTypeSelector.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    report: reportPropType,
    subject: subjectPropType,
}
