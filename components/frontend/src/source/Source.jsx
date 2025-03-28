import HistoryIcon from "@mui/icons-material/History"
import SettingsIcon from "@mui/icons-material/Settings"
import Grid from "@mui/material/Grid"
import { bool, func, object, oneOfType, string } from "prop-types"
import { useContext } from "react"

import { delete_source, set_source_attribute } from "../api/source"
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

function select_sources_parameter_keys(changed_fields, source_uuid) {
    return changed_fields
        ? changed_fields.filter((field) => field.source_uuid === source_uuid).map((field) => field.parameter_key)
        : []
}

function SourceButtonRow({ first_source, last_source, reload, source_uuid }) {
    const deleteButton = <DeleteButton itemType="source" onClick={() => delete_source(source_uuid, reload)} />
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingBottom={1} paddingLeft={0} paddingRight={0} paddingTop={2} rightButton={deleteButton}>
                    <ReorderButtonGroup
                        first={first_source}
                        last={last_source}
                        moveable="source"
                        onClick={(direction) => {
                            set_source_attribute(source_uuid, "position", direction, reload)
                        }}
                    />
                </ButtonRow>
            }
        />
    )
}
SourceButtonRow.propTypes = {
    first_source: bool,
    last_source: bool,
    reload: func,
    source_uuid: string,
}

function Parameters({
    changed_fields,
    config_error,
    connection_error,
    metric,
    parse_error,
    reload,
    report,
    source,
    source_uuid,
}) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const source_type = dataModel.sources[source.type]
    return (
        <Grid container alignItems="flex-start" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <SourceType
                    metric_type={metric.type}
                    set_source_attribute={(a, v) => set_source_attribute(source_uuid, a, v, reload)}
                    source_uuid={source_uuid}
                    source_type={source.type}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="source-name"
                    label="Source name"
                    placeholder={source_type.name}
                    onChange={(value) => set_source_attribute(source_uuid, "name", value, reload)}
                    value={source.name}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                <SourceParameters
                    changed_param_keys={select_sources_parameter_keys(changed_fields, source_uuid)}
                    metric={metric}
                    reload={reload}
                    report={report}
                    source={source}
                    source_uuid={source_uuid}
                />
            </Grid>
            {connection_error && (
                <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                    <WarningMessage pre title="Connection error">
                        {connection_error}
                    </WarningMessage>
                </Grid>
            )}
            {parse_error && (
                <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                    <WarningMessage pre title="Parse error">
                        {parse_error}
                    </WarningMessage>
                </Grid>
            )}
            {config_error && (
                <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                    <WarningMessage title="Configuration error">{config_error}</WarningMessage>
                </Grid>
            )}
        </Grid>
    )
}
Parameters.propTypes = {
    changed_fields: stringsPropType,
    config_error: oneOfType([object, string]),
    connection_error: string,
    metric: metricPropType,
    parse_error: string,
    reload: func,
    report: reportPropType,
    source: sourcePropType,
    source_uuid: string,
}

export function Source({
    changed_fields,
    first_source,
    last_source,
    measurement_source,
    metric,
    reload,
    report,
    settings,
    source_uuid,
}) {
    const dataModel = useContext(DataModel)
    const source = metric.sources[source_uuid]
    const sourceName = getSourceName(source, dataModel)
    const metricName = getMetricName(metric, dataModel)
    const connectionError = measurement_source?.connection_error || ""
    const parseError = measurement_source?.parse_error || ""
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
                    <HyperLink url={referenceDocumentationURL(sourceName)}>{sourceName}</HyperLink>.
                </li>
                <li>
                    Change the type of this source to a type that supports{" "}
                    <HyperLink url={referenceDocumentationURL(metricName)}>{metricName}</HyperLink>.
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
                uuid={source_uuid}
            >
                <Parameters
                    metric={metric}
                    source={source}
                    source_uuid={source_uuid}
                    connection_error={connectionError}
                    parse_error={parseError}
                    config_error={configError}
                    report={report}
                    changed_fields={changed_fields}
                    reload={reload}
                />
                <ChangeLog source_uuid={source_uuid} timestamp={report.timestamp} />
            </Tabs>
            <SourceButtonRow
                first_source={first_source}
                last_source={last_source}
                reload={reload}
                source_uuid={source_uuid}
            />
        </>
    )
}
Source.propTypes = {
    changed_fields: stringsPropType,
    first_source: bool,
    last_source: bool,
    measurement_source: measurementSourcePropType,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    source_uuid: string,
}
