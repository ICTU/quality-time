import { Stack } from "@mui/material"
import { func, string } from "prop-types"
import { useContext, useRef } from "react"

import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SnackbarContext } from "../context/Snackbar"
import { reportPropType, sourcePropType } from "../sharedPropTypes"
import { SourceParameter } from "../source/SourceParameter"
import { SourceTypeRichDescription } from "../source/SourceTypeSelector"
import { pluralize } from "../utils"
import { InfoMessage } from "../widgets/WarningMessage"

function reloadAfterMassEditSource(json, reload, showMessage) {
    const nrSources = json.nr_sources_mass_edited
    if (nrSources > 0) {
        showMessage({
            severity: "info",
            title: "Mass edit",
            description: `Changed ${nrSources} ${pluralize("source", nrSources)}`,
        })
    }
    reload(json)
}

export function LocationParameters({ reload, report, source, sourceUuid }) {
    const dataModel = useContext(DataModelContext)
    const showMessageRef = useRef(useContext(SnackbarContext))
    const sourceType = dataModel.sources[source.type]
    const allParameters = sourceType.parameters
    const defaultLocationParameterKeys = ["url", "landing_url", "username", "password", "private_token"]
    const locationParameterKeys = sourceType?.parameter_layout?.location?.parameters ?? defaultLocationParameterKeys
    let parameters
    if (new Set(Object.keys(allParameters)).intersection(new Set(locationParameterKeys)).size === 0) {
        parameters = <InfoMessage title="No location parameters">This source has no location parameters.</InfoMessage>
    } else {
        parameters = locationParameterKeys.map((key) => (
            <SourceParameter
                editScope="report"
                key={key}
                report={report}
                source={source}
                sourceUuid={sourceUuid}
                parameter={allParameters[key]}
                parameterKey={key}
                parameterValue={source?.parameters?.[key]}
                reload={(json) => reloadAfterMassEditSource(json, reload, showMessageRef.current)}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
            />
        ))
    }
    return (
        <Stack spacing={2} margin="10px">
            <SourceTypeRichDescription sourceTypeKey={source.type} />
            {parameters}
        </Stack>
    )
}
LocationParameters.propTypes = {
    reload: func,
    report: reportPropType,
    source: sourcePropType,
    sourceUuid: string,
}
