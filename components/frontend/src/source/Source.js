import { useContext } from 'react';
import PropTypes from 'prop-types';
import { Grid, Menu } from 'semantic-ui-react';
import { Icon, Label, Tab } from '../semantic_ui_react_wrappers';
import { StringInput } from '../fields/StringInput';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { HyperLink } from '../widgets/HyperLink';
import { delete_source, set_source_attribute } from '../api/source';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { SourceParameters } from './SourceParameters';
import { SourceType } from './SourceType';
import { SourceTypeHeader } from './SourceTypeHeader';
import { ErrorMessage } from '../errorMessage';
import { FocusableTab } from '../widgets/FocusableTab';
import { get_metric_name, get_source_name } from '../utils';
import { measurementSourceType, metricPropType, reportPropType, stringsPropType } from '../sharedPropTypes';

function select_sources_parameter_keys(changed_fields, source_uuid) {
    return changed_fields ? changed_fields.filter((field) => field.source_uuid === source_uuid).map((field) => field.parameter_key) : []
}

function ButtonGridRow({ first_source, last_source, source_uuid, reload }) {
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <div style={{ marginTop: "20px" }}>
                <Grid.Row>
                    <Grid.Column>
                        <ReorderButtonGroup first={first_source} last={last_source} moveable="source"
                            onClick={(direction) => { set_source_attribute(source_uuid, "position", direction, reload) }} />
                        <DeleteButton itemType="source" onClick={() => delete_source(source_uuid, reload)} />
                    </Grid.Column>
                </Grid.Row>
            </div>}
        />
    )
}

function Parameters({ metric, source, source_uuid, config_error, connection_error, parse_error, report, changed_fields, reload }) {
    const dataModel = useContext(DataModel)
    const source_type = dataModel.sources[source.type];
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
            <Grid.Row columns={2}>
                <SourceParameters
                    changed_param_keys={select_sources_parameter_keys(changed_fields, source_uuid)}
                    metric={metric}
                    reload={reload}
                    report={report}
                    source={source}
                    source_uuid={source_uuid}
                />
            </Grid.Row>
            {connection_error && <ErrorMessage title="Connection error" message={connection_error} />}
            {parse_error && <ErrorMessage title="Parse error" message={parse_error} />}
            {config_error && <ErrorMessage title="Configuration error" message={config_error} formatAsText={true} />}
        </Grid>
    )
}

export function Source({ metric, source_uuid, first_source, last_source, measurement_source, report, changed_fields, reload }) {
    const dataModel = useContext(DataModel)
    const source = metric.sources[source_uuid];
    const sourceType = dataModel.sources[source.type];
    const sourceName = get_source_name(source, dataModel);
    const metricName = get_metric_name(metric, dataModel);
    const connectionError = measurement_source?.connection_error || "";
    const parseError = measurement_source?.parse_error || "";
    const referenceManualURL = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html`;
    const configErrorMessage = <>
        <p>
            {sourceName} cannot be used to measure {metricName}. This configuration error occurs if the type of a
            metric is changed to a metric type that is not supported by the configured source type(s).
        </p>
        <p>
            There are several ways to fix this:
        </p>
        <ul>
            <li>Change the type of the metric (back) to a type that is supported by <HyperLink url={`${referenceManualURL}#${source.type}`}>{sourceName}</HyperLink>.</li>
            <li>Change the type of this source to a type that supports <HyperLink url={`${referenceManualURL}#${metric.type}`}>{metricName}</HyperLink>.</li>
            <li>Move this source to another metric.</li>
            <li>Remove this source altogether.</li>
        </ul>
        <p>
            As {sourceName} cannot be used to measure {metricName}, no source parameters are currently visible. Any
            source parameters configured previously will become visible again when the metric type is changed back to
            the previous metric type.
        </p>
    </>
    const configError = dataModel.metrics[metric.type].sources.includes(source.type) ? "" : configErrorMessage
    const configurationTabLabel = configError || connectionError || parseError ? <Label color='red'>{"Configuration"}</Label> : "Configuration";
    const panes = [
        {
            menuItem: <Menu.Item key="configuration"><Icon name="settings" /><FocusableTab>{configurationTabLabel}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <Parameters metric={metric} source={source} source_uuid={source_uuid} connection_error={connectionError}
                    parse_error={parseError} config_error={configError} report={report} changed_fields={changed_fields} reload={reload} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="changelog"><Icon name="history" /><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <ChangeLog source_uuid={source_uuid} timestamp={report.timestamp} />
            </Tab.Pane>
        }
    ];
    return (
        <>
            <SourceTypeHeader metricTypeId={metric.type} sourceTypeId={source.type} sourceType={sourceType} />
            <Tab panes={panes} />
            <ButtonGridRow first_source={first_source} last_source={last_source} reload={reload} source_uuid={source_uuid} />
        </>
    )
}
Source.propTypes = {
    metric: metricPropType,
    source_uuid: PropTypes.string,
    first_source: PropTypes.bool,
    last_source: PropTypes.bool,
    measurement_source: measurementSourceType,
    report: reportPropType,
    changed_fields: stringsPropType,
    reload: PropTypes.func,
}
