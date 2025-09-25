import HistoryIcon from "@mui/icons-material/History"
import SettingsIcon from "@mui/icons-material/Settings"
import Grid from "@mui/material/Grid"
import { bool, func, object, oneOfType, string } from "prop-types"
import { useContext } from "react"

import { deleteSource, setSourceAttribute } from "../api/source"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions, ReadOnlyOrEditable } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import {
    measurementSourcePropType,
    metricPropType,
    reportPropType,
    settingsPropType,
    sourcePropType,
    stringsPropType,
} from "../sharedPropTypes"
import { getMetricName, getSourceName, referenceDocumentationURL } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { ReorderButtonGroup } from "../widgets/buttons/ReorderButtonGroup"
import { HyperLink } from "../widgets/HyperLink"
import { Tabs } from "../widgets/Tabs"
import { WarningMessage } from "../widgets/WarningMessage"
import { SourceParameters } from "./SourceParameters"
import { SourceType } from "./SourceType"

function selectSourcesParameterKeys(changedFields, sourceUuid) {
    return changedFields
        ? changedFields.filter((field) => field.source_uuid === sourceUuid).map((field) => field.parameter_key)
        : []
}

function SourceButtonRow({ firstSource, lastSource, reload, sourceUuid }) {
    const deleteButton = <DeleteButton itemType="source" onClick={() => deleteSource(sourceUuid, reload)} />
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingBottom={1} paddingLeft={0} paddingRight={0} paddingTop={2} rightButton={deleteButton}>
                    <ReorderButtonGroup
                        first={firstSource}
                        last={lastSource}
                        moveable="source"
                        onClick={(direction) => setSourceAttribute(sourceUuid, "position", direction, reload)}
                    />
                </ButtonRow>
            }
        />
    )
}
SourceButtonRow.propTypes = {
    firstSource: bool,
    lastSource: bool,
    reload: func,
    sourceUuid: string,
}

function Parameters({
    changedFields,
    configError,
    connectionError,
    metric,
    parseError,
    reload,
    report,
    source,
    sourceUuid,
}) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const sourceType = dataModel.sources[source.type]
    return (
        <Grid container alignItems="flex-start" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <SourceType
                    metricType={metric.type}
                    setSourceAttribute={(a, v) => setSourceAttribute(sourceUuid, a, v, reload)}
                    sourceUuid={sourceUuid}
                    sourceType={source.type}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="source-name"
                    label="Source name"
                    placeholder={sourceType.name}
                    onChange={(value) => setSourceAttribute(sourceUuid, "name", value, reload)}
                    value={source.name}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                <SourceParameters
                    changedParamKeys={selectSourcesParameterKeys(changedFields, sourceUuid)}
                    metric={metric}
                    reload={reload}
                    report={report}
                    source={source}
                    sourceUuid={sourceUuid}
                />
            </Grid>
            {connectionError && (
                <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                    <WarningMessage pre title="Connection error">
                        {connectionError}
                    </WarningMessage>
                </Grid>
            )}
            {parseError && (
                <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                    <WarningMessage pre title="Parse error">
                        {parseError}
                    </WarningMessage>
                </Grid>
            )}
            {configError && (
                <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                    <WarningMessage title="Configuration error">{configError}</WarningMessage>
                </Grid>
            )}
        </Grid>
    )
}
Parameters.propTypes = {
    changedFields: stringsPropType,
    configError: oneOfType([object, string]),
    connectionError: string,
    metric: metricPropType,
    parseError: string,
    reload: func,
    report: reportPropType,
    source: sourcePropType,
    sourceUuid: string,
}

export function Source({
    changedFields,
    firstSource,
    lastSource,
    measurementSource,
    metric,
    reload,
    report,
    settings,
    sourceUuid,
}) {
    const dataModel = useContext(DataModel)
    const source = metric.sources[sourceUuid]
    const sourceName = getSourceName(source, dataModel)
    const metricName = getMetricName(metric, dataModel)
    const connectionError = measurementSource?.connection_error || ""
    const parseError = measurementSource?.parse_error || ""
    const configErrorMessage = (
        <>
            <p>
                {sourceName} cannot be used to measure {metricName}. This configuration error occurs if the type of a
                metric is changed to a metric type that is not supported by the configured source type(s).
            </p>
            <p>There are several ways to fix this:</p>
            <ul>
                <li>
                    Change the type of the metric (back) to a type that is supported by{" "}
                    <HyperLink url={referenceDocumentationURL(dataModel.metrics[metric.type].name)}>
                        {sourceName}
                    </HyperLink>
                    .
                </li>
                <li>
                    Change the type of this source to a type that supports{" "}
                    <HyperLink url={referenceDocumentationURL(dataModel.sources[source.type].name)}>
                        {metricName}
                    </HyperLink>
                    .
                </li>
                <li>Move this source to another metric.</li>
                <li>Remove this source altogether.</li>
            </ul>
            <p>
                As {sourceName} cannot be used to measure {metricName}, no source parameters are currently visible. Any
                source parameters configured previously will become visible again when the metric type is changed back
                to the previous metric type.
            </p>
        </>
    )
    const configError = dataModel.metrics[metric.type].sources.includes(source.type) ? "" : configErrorMessage
    const anyError = Boolean(configError || connectionError || parseError)
    return (
        <>
            <Tabs
                settings={settings}
                tabs={[
                    { error: anyError, label: "Configuration", icon: <SettingsIcon /> },
                    { label: "Changelog", icon: <HistoryIcon /> },
                ]}
                uuid={sourceUuid}
            >
                <Parameters
                    metric={metric}
                    source={source}
                    sourceUuid={sourceUuid}
                    connectionError={connectionError}
                    parseError={parseError}
                    configError={configError}
                    report={report}
                    changedFields={changedFields}
                    reload={reload}
                />
                <ChangeLog sourceUuid={sourceUuid} timestamp={report.timestamp} />
            </Tabs>
            <SourceButtonRow
                firstSource={firstSource}
                lastSource={lastSource}
                reload={reload}
                sourceUuid={sourceUuid}
            />
        </>
    )
}
Source.propTypes = {
    changedFields: stringsPropType,
    firstSource: bool,
    lastSource: bool,
    measurementSource: measurementSourcePropType,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    sourceUuid: string,
}
