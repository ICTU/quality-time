import { Chip, Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { dataModelPropType, sourceTypePropType } from "../sharedPropTypes"
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

function sourceTypeOption(key, sourceType) {
    return {
        key: key,
        text: sourceType.name,
        value: key,
        content: (
            <Stack direction="row">
                <span style={{ paddingRight: "10px" }}>
                    <Logo logo={key} alt={sourceType.name} />
                </span>
                <p>
                    {sourceType.name}
                    {sourceType.deprecated && <Chip color="warning" label="Deprecated" sx={{ marginLeft: "8px" }} />}
                    <Typography variant="body2">{sourceTypeDescription(sourceType)}</Typography>
                </p>
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
    const options = sourceTypeOptions(dataModel, metric_type)
    const sourceTypes = options.map((option) => option.key)
    if (!sourceTypes.includes(source_type)) {
        options.push(sourceTypeOption(source_type, dataModel.sources[source_type]))
    }
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Source type"
            options={options}
            set_value={(value) => set_source_attribute("type", value)}
            value={source_type}
        />
    )
}
SourceType.propTypes = {
    metric_type: string,
    set_source_attribute: func,
    source_type: string,
}
