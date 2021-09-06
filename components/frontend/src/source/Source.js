import React from 'react';
import { Grid, Header, Icon } from 'semantic-ui-react';
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

function AttributesRow(props) {
    return (
        <Grid.Row columns={2}>
            <Grid.Column>
                <SourceType
                    datamodel={props.datamodel}
                    metric_type={props.metric_type} 
                    set_source_attribute={(a, v) => set_source_attribute(props.source_uuid, a, v, props.reload)} 
                    source_uuid={props.source_uuid}
                    source_type={props.source.type}
                />
            </Grid.Column>
            <Grid.Column>
                <StringInput
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    id="source-name"
                    label="Source name"
                    placeholder={props.source_type.name}
                    set_value={(value) => set_source_attribute(props.source_uuid, "name", value, props.reload)}
                    value={props.source.name}
                />
            </Grid.Column>
        </Grid.Row>
    )
}

function ParametersRow(props) {
    return (
        <Grid.Row columns={2}>
            <SourceParameters {...props} />
        </Grid.Row>
    )
}

function ChangeLogRow(props) {
    return (
        <Grid.Row>
            <Grid.Column>
                <ChangeLog {...props} />
            </Grid.Column>
        </Grid.Row >
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

export function Source(props) {
    const source_type = props.datamodel.sources[props.source.type];
    return (
        <>
            <SourceHeader source={props.source} source_type={source_type} />
            <Grid stackable>
                <AttributesRow datamodel={props.datamodel} reload={props.reload} source={props.source} source_type={source_type} source_uuid={props.source_uuid} metric_type={props.metric_type} />
                <ParametersRow
                    changed_param_keys={select_sources_parameter_keys(props.changed_fields, props.source_uuid)}
                    datamodel={props.datamodel}
                    metric_type={props.metric_type}
                    metric_unit={props.metric_unit}
                    reload={props.reload}
                    report={props.report}
                    source={props.source}
                    source_uuid={props.source_uuid}
                />
                {props.connection_error && <ErrorMessage title="Connection error" message={props.connection_error} />}
                {props.parse_error && <ErrorMessage title="Parse error" message={props.parse_error} />}
                <ChangeLogRow report_uuid={props.report_uuid} source_uuid={props.source_uuid} timestamp={props.report.timestamp} />
                <ButtonGridRow first_source={props.first_source} last_source={props.last_source} reload={props.reload} source_uuid={props.source_uuid} />
            </Grid>
        </>
    )
}
