import { bool, func, object, oneOfType, string } from "prop-types"
import { useContext } from "react"
import { Grid } from "semantic-ui-react"

import { delete_source, set_source_attribute } from "../api/source"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { ErrorMessage } from "../errorMessage"
import { StringInput } from "../fields/StringInput"
import { Tab } from "../semantic_ui_react_wrappers"
import {
    measurementSourcePropType,
    metricPropType,
    reportPropType,
    sourcePropType,
    stringsPropType,
} from "../sharedPropTypes"
import { getMetricName, getSourceName } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { ReorderButtonGroup } from "../widgets/buttons/ReorderButtonGroup"
import { HyperLink } from "../widgets/HyperLink"
import { changelogTabPane, configurationTabPane } from "../widgets/TabPane"
import { SourceParameters } from "./SourceParameters"
import { SourceType } from "./SourceType"
import { SourceTypeHeader } from "./SourceTypeHeader"

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
                <ButtonRow rightButton={deleteButton}>
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
    const source_type = dataModel.sources[source.type]
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SourceType
                        metric_type={metric.type}
                        set_source_attribute={(a, v) => set_source_attribute(source_uuid, a, v, reload)}
                        source_uuid={source_uuid}
                        source_type={source.type}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        id="source-name"
                        label="Source name"
                        placeholder={source_type.name}
                        set_value={(value) => set_source_attribute(source_uuid, "name", value, reload)}
                        value={source.name}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <SourceParameters
                        changed_param_keys={select_sources_parameter_keys(changed_fields, source_uuid)}
                        metric={metric}
                        reload={reload}
                        report={report}
                        source={source}
                        source_uuid={source_uuid}
                    />
                </Grid.Column>
            </Grid.Row>
            {connection_error && <ErrorMessage title="Connection error" message={connection_error} />}
            {parse_error && <ErrorMessage title="Parse error" message={parse_error} />}
            {config_error && <ErrorMessage title="Configuration error" message={config_error} formatAsText={true} />}
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
    source_uuid,
}) {
    const dataModel = useContext(DataModel)
    const source = metric.sources[source_uuid]
    const sourceType = dataModel.sources[source.type]
    const sourceName = getSourceName(source, dataModel)
    const metricName = getMetricName(metric, dataModel)
    const connectionError = measurement_source?.connection_error || ""
    const parseError = measurement_source?.parse_error || ""
    const referenceManualURL = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html`
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
                    <HyperLink url={`${referenceManualURL}#${source.type}`}>{sourceName}</HyperLink>.
                </li>
                <li>
                    Change the type of this source to a type that supports{" "}
                    <HyperLink url={`${referenceManualURL}#${metric.type}`}>{metricName}</HyperLink>.
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
    const panes = [
        configurationTabPane(
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
            />,
            { error: Boolean(configError || connectionError || parseError) },
        ),
        changelogTabPane(<ChangeLog source_uuid={source_uuid} timestamp={report.timestamp} />),
    ]
    return (
        <>
            <SourceTypeHeader metricTypeId={metric.type} sourceTypeId={source.type} sourceType={sourceType} />
            <Tab panes={panes} />
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
    source_uuid: string,
}
