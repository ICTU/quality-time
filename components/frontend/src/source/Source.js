import React, { useContext } from 'react';
import { Grid, Label, Menu } from 'semantic-ui-react';
import { Header } from '../semantic_ui_react_wrappers/Header';
import { Icon } from '../semantic_ui_react_wrappers/Icon';
import { Tab } from '../semantic_ui_react_wrappers/Tab';
import { StringInput } from '../fields/StringInput';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { HyperLink } from '../widgets/HyperLink';
import { delete_source, set_source_attribute } from '../api/source';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { Logo } from './Logo';
import { SourceParameters } from './SourceParameters';
import { SourceType } from './SourceType';
import { ErrorMessage } from '../errorMessage';
import { FocusableTab } from '../widgets/FocusableTab';

function select_sources_parameter_keys(changed_fields, source_uuid) {
    return changed_fields ? changed_fields.filter((field) => field.source_uuid === source_uuid).map((field) => field.parameter_key) : []
}

function SourceHeader({ source }) {
    const dataModel = useContext(DataModel)
    const source_type = dataModel.sources[source.type];
    return (
        <Header>
            <Header.Content>
                <Logo logo={source.type} alt={source_type.name} />
                {source_type.name}
                <Header.Subheader>
                    {source_type.description}
                    {source_type.url && <HyperLink url={source_type.url}><Icon name="external" link /></HyperLink>}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}

function ButtonGridRow({ first_source, last_source, source_uuid, reload }) {
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <div style={{ marginTop: "20px" }}>
                <Grid.Row>
                    <Grid.Column>
                        <ReorderButtonGroup first={first_source} last={last_source} moveable="source"
                            onClick={(direction) => { set_source_attribute(source_uuid, "position", direction, reload) }} />
                        <DeleteButton item_type="source" onClick={() => delete_source(source_uuid, reload)} />
                    </Grid.Column>
                </Grid.Row>
            </div>}
        />
    )
}

function Parameters({ metric, source, source_uuid, connection_error, parse_error, report, changed_fields, reload }) {
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
        </Grid>
    )
}

export function Source({ metric, source_uuid, first_source, last_source, measurement_source, report, changed_fields, reload }) {
    const source = metric.sources[source_uuid];
    const connectionError = measurement_source?.connection_error || "";
    const parseError = measurement_source?.parse_error || "";
    const configurationTabLabel = connectionError || parseError ? <Label color='red'>{"Configuration"}</Label> : "Configuration";
    const panes = [
        {
            menuItem: <Menu.Item key="configuration"><Icon name="settings" /><FocusableTab>{configurationTabLabel}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <Parameters metric={metric} source={source} source_uuid={source_uuid} connection_error={connectionError}
                parse_error={parseError} report={report} changed_fields={changed_fields} reload={reload} />
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
            <SourceHeader source={source} />
            <Tab panes={panes} />
            <ButtonGridRow first_source={first_source} last_source={last_source} reload={reload} source_uuid={source_uuid} />
        </>
    )
}
