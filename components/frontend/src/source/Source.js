import React from 'react';
import { Grid, Header, Icon, Label, Menu, Tab } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { HyperLink } from '../widgets/HyperLink';
import { delete_source, set_source_attribute } from '../api/source';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { Logo } from './Logo';
import { SourceParameters } from './SourceParameters';
import { SourceType } from './SourceType';
import { ErrorMessage } from '../errorMessage';
import { FocusableTab } from '../widgets/FocusableTab';

function select_sources_parameter_keys(changed_fields, source_uuid) {
    return changed_fields ? changed_fields.filter((field) => field.source_uuid === source_uuid).map((field) => field.parameter_key) : []
}

function SourceHeader(props) {
    return (
        <Header>
            <Header.Content>
                <Logo logo={props.source.type} alt={props.source_type.name} />
                {props.source_type.name}
                <Header.Subheader>
                    {props.source_type.description}
                    {props.source_type.url && <HyperLink url={props.source_type.url}><Icon name="external" link /></HyperLink>}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}

function SourceTypeAndName({ datamodel, source, source_uuid, metric_type, reload }) {
    const source_type = datamodel.sources[source.type];
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SourceType
                        datamodel={datamodel}
                        metric_type={metric_type}
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
        </Grid>
    )
}

function ButtonGridRow(props) {
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Grid.Row>
                <Grid.Column>
                    <ReorderButtonGroup first={props.first_source} last={props.last_source} moveable="source"
                        onClick={(direction) => { set_source_attribute(props.source_uuid, "position", direction, props.reload) }} />
                    <DeleteButton item_type="source" onClick={() => delete_source(props.source_uuid, props.reload)} />
                </Grid.Column>
            </Grid.Row>}
        />
    )
}

function Parameters({ datamodel, source, source_uuid, connection_error, parse_error, metric_type, metric_unit, report, changed_fields, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <SourceParameters
                    changed_param_keys={select_sources_parameter_keys(changed_fields, source_uuid)}
                    datamodel={datamodel}
                    metric_type={metric_type}
                    metric_unit={metric_unit}
                    reload={reload}
                    report={report}
                    source={source}
                    source_uuid={source_uuid}
                />
            </Grid.Row>
            {connection_error && <ErrorMessage title="Connection error" message={connection_error} />}
            {parse_error && <ErrorMessage title="Parse error" message={parse_error} />}
        </Grid >
    )
}

export function Source({ datamodel, source, source_uuid, first_source, last_source, connection_error, parse_error, metric_type, metric_unit, report, changed_fields, reload }) {
    const source_type = datamodel.sources[source.type];
    const parameter_menu_item = connection_error || parse_error ? <Label color='red'>{"Parameters"}</Label> : "Parameters";
    const panes = [
        {
            menuItem: <Menu.Item><FocusableTab>{"Source type and name"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <SourceTypeAndName datamodel={datamodel} source={source} source_uuid={source_uuid} metric_type={metric_type} reload={reload} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item><FocusableTab>{parameter_menu_item}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <Parameters datamodel={datamodel} source={source} source_uuid={source_uuid}
                    connection_error={connection_error} parse_error={parse_error} metric_type={metric_type}
                    metric_unit={metric_unit} report={report} changed_fields={changed_fields} reload={reload} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <ChangeLog report_uuid={report.report_uuid} source_uuid={source_uuid} timestamp={report.timestamp} />
            </Tab.Pane>
        }
    ];
    return (
        <>
            <SourceHeader source={source} source_type={source_type} />
            <Tab panes={panes} />
            <div style={{ marginTop: "20px" }}>
                <ButtonGridRow first_source={first_source} last_source={last_source} reload={reload} source_uuid={source_uuid} />
            </div>
        </>
    )
}
