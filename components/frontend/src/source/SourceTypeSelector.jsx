import { Chip, InputAdornment, Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { dataModelPropType, sourceTypePropType } from "../sharedPropTypes"
import { referenceDocumentationURL } from "../utils"
import { ItemTypeSelector } from "../widgets/ItemTypeSelector"
import { ItemTypeSelectorTextField } from "../widgets/ItemTypeSelectorTextField"
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
    const dataModel = useContext(DataModelContext)
    const sourceType = dataModel.sources[sourceTypeKey]
    return (
        <Stack direction="row" sx={{ maxWidth: "40vw" }}>
            <span style={{ paddingRight: "10px" }}>
                <Logo logo={sourceTypeKey} alt={sourceType.name} />
            </span>
            <Stack direction="column">
                <Stack direction="row" sx={{ alignItems: "center" }}>
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

export function SourceTypeSelector({ metricType, setSourceAttribute, sourceType }) {
    const dataModel = useContext(DataModelContext)
    const permissions = useContext(PermissionsContext)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const options = sourceTypeOptions(dataModel, metricType)
    const sourceTypes = options.map((option) => option.key)
    if (!sourceTypes.includes(sourceType)) {
        options.push(sourceTypeOption(sourceType, dataModel.sources[sourceType]))
    }
    const sourceTypeDocumentation = dataModel.sources[sourceType]?.documentation
    const hasExtraDocs = sourceTypeDocumentation?.generic || sourceTypeDocumentation?.[metricType]
    const howToConfigure = ` for ${hasExtraDocs ? "additional " : ""}information on how to configure this source type.`
    const sourceTypeName = dataModel.sources[sourceType].name
    const sourceTypeDeprecated = dataModel.sources[sourceType].deprecated
    return (
        <ItemTypeSelector
            itemSubtypes={options}
            itemType="source"
            onClick={(value) => setSourceAttribute("type", value)}
            renderAnchor={(handleMenu) => (
                <ItemTypeSelectorTextField
                    disabled={disabled}
                    handleMenu={handleMenu}
                    helperText={
                        <>
                            <ReadTheDocsLink url={referenceDocumentationURL(sourceTypeName)} />
                            {howToConfigure}
                        </>
                    }
                    label="Source type"
                    startAdornment={
                        <InputAdornment position="start">
                            {sourceTypeDeprecated && (
                                <Chip color="warning" label="Deprecated" size="small" sx={{ marginRight: "10px" }} />
                            )}
                            <Logo logo={sourceType} alt={sourceTypeName} width="1em" height="1em" />
                        </InputAdornment>
                    }
                    value={sourceTypeName}
                />
            )}
        />
    )
}
SourceTypeSelector.propTypes = {
    metricType: string,
    setSourceAttribute: func,
    sourceType: string,
}
