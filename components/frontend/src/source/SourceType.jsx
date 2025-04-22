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

export function SourceTypeRichDescription({ sourceTypeKey }) {
    const dataModel = useContext(DataModel)
    const sourceType = dataModel.sources[sourceTypeKey]
    return (
        <Stack direction="row" sx={{ maxWidth: "40vw" }}>
            <span style={{ paddingRight: "10px" }}>
                <Logo logo={sourceTypeKey} alt={sourceType.name} />
            </span>
            <Stack direction="column">
                <Stack direction="row" alignItems="center">
                    {sourceType.name}
                    {sourceType.deprecated && <Chip color="warning" label="Deprecated" sx={{ marginLeft: "8px" }} />}
                </Stack>
                <Typography variant="body2" sx={{ whiteSpace: "normal" }}>
                    {sourceTypeDescription(sourceType)}
                </Typography>
            </Stack>
        </Stack>
    )
}
SourceTypeRichDescription.propTypes = {
    sourceTypeKey: string,
}

export function sourceTypeOption(key, sourceType) {
    return {
        key: key,
        text: sourceType.name,
        value: key,
        content: <SourceTypeRichDescription sourceTypeKey={key} />,
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

export function SourceType({ metricType, setSourceAttribute, sourceType }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const options = sourceTypeOptions(dataModel, metricType)
    const sourceTypes = options.map((option) => option.key)
    if (!sourceTypes.includes(sourceType)) {
        options.push(sourceTypeOption(sourceType, dataModel.sources[sourceType]))
    }
    const sourceTypeDocumentation = dataModel.sources[sourceType]?.documentation
    const hasExtraDocs = sourceTypeDocumentation?.generic || sourceTypeDocumentation?.[metricType]
    const howToConfigure = ` for ${hasExtraDocs ? "additional " : ""}information on how to configure this source type.`
    return (
        <TextField
            disabled={disabled}
            helperText={
                <>
                    <ReadTheDocsLink url={referenceDocumentationURL(sourceType)} />
                    {howToConfigure}
                </>
            }
            label="Source type"
            onChange={(value) => setSourceAttribute("type", value)}
            select
            value={sourceType}
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
    metricType: string,
    setSourceAttribute: func,
    sourceType: string,
}
