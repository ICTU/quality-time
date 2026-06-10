import { Stack } from "@mui/material"
import { bool, func, object, string } from "prop-types"
import { useContext } from "react"

import { setSourceLocationAttribute, setSourceLocationParameter } from "../api/source_location"
import { DataModelContext } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { availabilityMessagePropType, sourceLocationPropType } from "../sharedPropTypes"
import { SourceTypeRichDescription } from "../source/SourceType"
import { HyperLink } from "../widgets/HyperLink"

export const SOURCE_LOCATION_PARAMETER_KEYS = ["url", "landing_url", "username", "password", "private_token"]

function SourceLocationParameter({
    disabled,
    parameter,
    parameterKey,
    parameterValue,
    sourceLocationUuid,
    reload,
    warning,
}) {
    let helperText = null
    if (parameter?.help_url) {
        helperText = (
            <>
                See <HyperLink url={parameter.help_url}>{parameter.help_url}</HyperLink> for more information.
            </>
        )
    }
    if (parameter?.help) {
        helperText = parameter.help
    }
    return (
        <TextField
            disabled={disabled}
            error={parameter?.type === "url" && warning}
            helperText={helperText}
            label={parameter?.name}
            onChange={(value) => setSourceLocationParameter(sourceLocationUuid, parameterKey, value, reload)}
            placeholder={parameter?.placeholder || ""}
            required={parameter?.mandatory}
            type={parameter?.type === "password" ? "password" : "text"}
            value={parameterValue || ""}
        />
    )
}
SourceLocationParameter.propTypes = {
    disabled: bool,
    parameter: object,
    parameterKey: string,
    parameterValue: string,
    sourceLocationUuid: string,
    reload: func,
    warning: bool,
}

export function SourceLocationParameters({
    fieldWithUrlAvailabilityError,
    reload,
    sourceLocation,
    sourceLocationUuid,
}) {
    const dataModel = useContext(DataModelContext)
    const permissions = useContext(PermissionsContext)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const sourceType = dataModel.sources[sourceLocation.source_type]
    const parameterKeys = SOURCE_LOCATION_PARAMETER_KEYS.filter((parameterKey) =>
        Object.keys(sourceType?.parameters ?? {}).includes(parameterKey),
    )
    return (
        <Stack spacing={2} margin="10px">
            <SourceTypeRichDescription sourceTypeKey={sourceLocation.source_type} />
            <TextField
                disabled={disabled}
                id="source-location-name"
                label="Source location name"
                placeholder={sourceType?.name}
                onChange={(value) => setSourceLocationAttribute(sourceLocationUuid, "location_name", value, reload)}
                value={sourceLocation.location_name || ""}
            />
            {parameterKeys.map((parameterKey) => (
                <SourceLocationParameter
                    disabled={disabled}
                    key={parameterKey}
                    parameter={sourceType?.parameters?.[parameterKey]}
                    parameterKey={parameterKey}
                    parameterValue={sourceLocation[parameterKey]}
                    sourceLocationUuid={sourceLocationUuid}
                    reload={reload}
                    warning={
                        fieldWithUrlAvailabilityError?.source_uuid === sourceLocationUuid &&
                        fieldWithUrlAvailabilityError?.parameter_key === parameterKey
                    }
                />
            ))}
        </Stack>
    )
}
SourceLocationParameters.propTypes = {
    fieldWithUrlAvailabilityError: availabilityMessagePropType,
    reload: func,
    sourceLocation: sourceLocationPropType,
    sourceLocationUuid: string,
}
