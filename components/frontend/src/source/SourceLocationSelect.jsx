import { MenuItem, Stack, Typography } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { setSourceAttribute } from "../api/source"
import { DataModelContext } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { reportPropType, sourcePropType } from "../sharedPropTypes"
import { getSourceLocationName, getSourceTypeName, sourceTypeHasLocation } from "../utils"
import { InfoMessage } from "../widgets/WarningMessage"

export function SourceLocationSelect({ reload, report, source, sourceUuid }) {
    const dataModel = useContext(DataModelContext)
    const permissions = useContext(PermissionsContext)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    if (!sourceTypeHasLocation(dataModel, source.type)) {
        return null // The source type has no location parameters, so there is no source location to select
    }
    const options = Object.entries(report.source_locations ?? {}).filter(
        ([_sourceLocationUuid, sourceLocation]) => sourceLocation.source_type === source.type,
    )
    options.sort((option1, option2) =>
        getSourceLocationName(option1[1], dataModel).localeCompare(getSourceLocationName(option2[1], dataModel)),
    )
    if (options.length === 0) {
        return (
            <InfoMessage title="No source locations">
                There are no source locations for this source type yet. Expand the report title and add a source
                location in the &apos;Source locations&apos; tab.
            </InfoMessage>
        )
    }
    const sourceTypeName = getSourceTypeName(source, dataModel)
    return (
        <TextField
            disabled={disabled}
            helperText="The source location provides the URL and credentials needed to access the source"
            label="Source location"
            onChange={(value) => setSourceAttribute(sourceUuid, "source_location", value, reload)}
            required
            select
            value={source.source_location || ""}
        >
            {options.map(([sourceLocationUuid, sourceLocation]) => (
                <MenuItem key={sourceLocationUuid} value={sourceLocationUuid}>
                    <Stack direction="column">
                        {getSourceLocationName(sourceLocation, dataModel)}
                        <Typography variant="body2" sx={{ whiteSpace: "normal" }}>
                            {sourceTypeName}
                            {sourceLocation.url ? ` - ${sourceLocation.url}` : ""}
                        </Typography>
                    </Stack>
                </MenuItem>
            ))}
        </TextField>
    )
}
SourceLocationSelect.propTypes = {
    reload: func,
    report: reportPropType,
    source: sourcePropType,
    sourceUuid: string,
}
