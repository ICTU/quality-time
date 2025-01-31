import { Chip, MenuItem, Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { dataModelPropType, sourceTypePropType } from "../sharedPropTypes"
import { referenceDocumentationURL } from "../utils"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"
import { Logo } from "./Logo"

export function sourceTypeDescription(sourceType) {
    let description = sourceType.description
    if (sourceType.supported_versions_description) {
        description += ` Supported ${sourceType.name} versions: ${sourceType.supported_versions_description}.`
    }
    return description
}
sourceTypeDescription.propTypes = {
    sourceType: sourceTypePropType,
}

export function sourceTypeOption(key, sourceType) {
    return {
        key: key,
        text: sourceType.name,
        value: key,
        content: (
            <Stack direction="row" sx={{ maxWidth: "40vw" }}>
                <span style={{ paddingRight: "10px" }}>
                    <Logo logo={key} alt={sourceType.name} />
                </span>
                <Stack direction="column">
                    <Stack direction="row" alignItems="center">
                        {sourceType.name}
                        {sourceType.deprecated && (
                            <Chip color="warning" label="Deprecated" sx={{ marginLeft: "8px" }} />
                        )}
                    </Stack>
                    <Typography variant="body2" sx={{ whiteSpace: "normal" }}>
                        {sourceTypeDescription(sourceType)}
                    </Typography>
                </Stack>
            </Stack>
        ),
    }
}
sourceTypeOption.propTypes = {
    key: string,
    sourceType: sourceTypePropType,
}

export function sourceTypeOptions(dataModel, metricType) {
    // Return menu options for all sources that support the metric type
    return dataModel.metrics[metricType].sources.map((key) => sourceTypeOption(key, dataModel.sources[key]))
}
sourceTypeOptions.propTypes = {
    dataModel: dataModelPropType,
    metricType: string,
}

export function SourceType({ metric_type, set_source_attribute, source_type }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const options = sourceTypeOptions(dataModel, metric_type)
    const sourceTypes = options.map((option) => option.key)
    if (!sourceTypes.includes(source_type)) {
        options.push(sourceTypeOption(source_type, dataModel.sources[source_type]))
    }
    const sourceType = dataModel.sources[source_type]
    const hasExtraDocs = sourceType?.documentation?.generic || sourceType?.documentation?.[metric_type]
    const howToConfigure = ` for ${hasExtraDocs ? "additional " : ""}information on how to configure this source type.`
    return (
        <TextField
            disabled={disabled}
            helperText={
                <>
                    <ReadTheDocsLink url={referenceDocumentationURL(source_type)} />
                    {howToConfigure}
                </>
            }
            label="Source type"
            onChange={(value) => set_source_attribute("type", value)}
            select
            value={source_type}
        >
            {options.map((option) => (
                <MenuItem key={option.key} sx={{ width: "50vw" }} value={option.value}>
                    {option.content}
                </MenuItem>
            ))}
        </TextField>
    )
}
SourceType.propTypes = {
    metric_type: string,
    set_source_attribute: func,
    source_type: string,
}
