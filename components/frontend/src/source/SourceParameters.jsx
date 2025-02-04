import { Paper, Stack, Typography } from "@mui/material"
import Grid from "@mui/material/Grid2"
import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { metricPropType, reportPropType, sourcePropType, stringsPropType } from "../sharedPropTypes"
import { formatMetricScaleAndUnit } from "../utils"
import { SourceParameter } from "./SourceParameter"

// Default layout to be used when the user is time traveling to a version of the data model that has no parameter layouts
const DEFAULT_LAYOUT = { all: { name: "Source parameters", parameters: [] } }

function collectGroupedParameters(parameterLayout) {
    // Grouped parameters are source parameters that are explicitly part of a group
    let parameters = []
    Object.values(parameterLayout).forEach((parameterGroup) => {
        parameters.push(...parameterGroup.parameters)
    })
    return parameters
}

function collectRemainingParameters(allParameters, groupedParameters) {
    // Remaining parameters are source parameters that are not explicitly part of a group
    return Object.keys(allParameters).filter((parameterKey) => !groupedParameters.includes(parameterKey))
}

function applicableParameters(allParameters, remainingParameters, parameterGroup, metric) {
    // Return the applicable parameters for a parameter group
    const parameterKeys = parameterGroup.parameters.length > 0 ? parameterGroup.parameters : remainingParameters
    return parameterKeys.filter((parameterKey) => allParameters[parameterKey]?.metrics?.includes(metric.type))
}

export function SourceParameters({ changed_param_keys, metric, reload, report, source, source_uuid }) {
    const dataModel = useContext(DataModel)
    const metricUnit = formatMetricScaleAndUnit(metric, dataModel)
    const allParameters = dataModel.sources[source.type].parameters
    const parameterLayout = dataModel.sources[source.type].parameter_layout ?? DEFAULT_LAYOUT
    const groupedParameters = collectGroupedParameters(parameterLayout)
    const remainingParameters = collectRemainingParameters(allParameters, groupedParameters)
    const groups = Object.values(parameterLayout).map((parameterGroup) => {
        const parameterKeys = applicableParameters(allParameters, remainingParameters, parameterGroup, metric)
        if (parameterKeys.length === 0) {
            return null
        }
        const parameters = parameterKeys.map((parameterKey) => (
            <div key={parameterKey} style={{ paddingTop: "10px" }}>
                <SourceParameter
                    report={report}
                    source={source}
                    source_uuid={source_uuid}
                    parameter_key={parameterKey}
                    parameter_type={allParameters[parameterKey].type}
                    parameter_name={allParameters[parameterKey].name}
                    parameter_unit={allParameters[parameterKey].unit || metricUnit}
                    parameter_min={allParameters[parameterKey].min_value || null}
                    parameter_max={allParameters[parameterKey].max_value || null}
                    parameter_value={
                        source.parameters?.[parameterKey]
                            ? source.parameters[parameterKey]
                            : allParameters[parameterKey].default_value
                    }
                    parameter_values={allParameters[parameterKey].values || []}
                    help_url={allParameters[parameterKey].help_url}
                    help={allParameters[parameterKey].help}
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    placeholder={allParameters[parameterKey].placeholder || ""}
                    required={allParameters[parameterKey].mandatory}
                    warning={changed_param_keys?.indexOf(parameterKey) !== -1}
                    reload={reload}
                />
            </div>
        ))
        return (
            <Grid key={parameterGroup.name} size={{ xs: 1, sm: 1, md: 1 }}>
                <Paper elevation={2} sx={{ padding: "8px" }}>
                    <Stack direction="column" spacing={2}>
                        <Typography variant="h3">{parameterGroup.name}</Typography>
                        {parameters}
                    </Stack>
                </Paper>
            </Grid>
        )
    })
    return (
        <Grid container alignItems="flex-start" columns={{ xs: 1, sm: 1, md: 2 }} spacing={{ xs: 1, sm: 2, md: 3 }}>
            {groups}
        </Grid>
    )
}
SourceParameters.propTypes = {
    changed_param_keys: stringsPropType,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    source: sourcePropType,
    source_uuid: string,
}
