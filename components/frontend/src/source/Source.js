import React from 'react';
import { Grid, Header, Icon, Message } from 'semantic-ui-react';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';
import { StringInput } from '../fields/StringInput';
import { Logo } from '../logos/Logo';
import { ChangeLog } from '../changelog/ChangeLog';
import { CopyButton, DeleteButton } from '../widgets/Button';
import { copy_source, delete_source, set_source_attribute } from '../api/source';
import { ReadOnlyOrEditable } from '../context/ReadOnly';

function select_sources_parameter_keys(changed_fields, source_uuid) {
    return changed_fields ? changed_fields.filter((field) => field.source_uuid === source_uuid).map((field) => field.parameter_key) : []
}

export function Source(props) {
    const source_type = props.datamodel.sources[props.source.type];

    function SourceHeader() {
        return (
            <Header>
                <Header.Content>
                    <Logo logo={props.source.type} alt={source_type.name} />
                    {source_type.name}
                    <Header.Subheader>
                        {source_type.description}
                        {source_type.url && <a href={source_type.url} target="_blank" title="Opens new window or tab" rel="noopener noreferrer"><Icon name="external" link /></a>}
                    </Header.Subheader>
                </Header.Content>
            </Header>
        )
    }

    function ErrorMessage(title, message) {
        return (
            <Grid.Row columns={1}>
                <Grid.Column>
                    <Message negative>
                        <Message.Header>{title}</Message.Header>
                        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{message}</pre>
                    </Message>
                </Grid.Column>
            </Grid.Row>
        )
    }

    return (
        <>
            <SourceHeader />
            <Grid stackable>
                <Grid.Row columns={2}>
                    <Grid.Column>
                        <SourceType
                            source_type={props.source.type}
                            metric_type={props.metric_type} datamodel={props.datamodel}
                            set_source_attribute={(a, v) => set_source_attribute(props.report.report_uuid, props.source_uuid, a, v, props.reload)} />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            label="Source name"
                            placeholder={source_type.name}
                            set_value={(value) => set_source_attribute(props.report.report_uuid, props.source_uuid, "name", value, props.reload)}
                            value={props.source.name}
                        />
                    </Grid.Column>
                    <SourceParameters
                        datamodel={props.datamodel}
                        metric_type={props.metric_type}
                        metric_unit={props.metric_unit}
                        reload={props.reload}
                        report={props.report}
                        source={props.source}
                        source_uuid={props.source_uuid}
                        changed_param_keys={select_sources_parameter_keys(props.changed_fields, props.source_uuid)}
                    />
                </Grid.Row>
                {props.connection_error && <ErrorMessage title="Connection error" message={props.connection_error} />}
                {props.parse_error && <ErrorMessage title="Parse error" message={props.parse_error} />}
                <Grid.Row>
                    <Grid.Column>
                        <ChangeLog
                            report_uuid={props.report.report_uuid}
                            source_uuid={props.source_uuid}
                            timestamp={props.report.timestamp}
                        />
                    </Grid.Column>
                </Grid.Row>
                <ReadOnlyOrEditable editableComponent={
                    <Grid.Row columns={2}>
                        <Grid.Column>
                            <CopyButton
                                item_type='source'
                                onClick={() => copy_source(props.report.report_uuid, props.source_uuid, props.reload)}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <DeleteButton
                                item_type='source'
                                onClick={() => delete_source(props.report.report_uuid, props.source_uuid, props.reload)}
                            />
                        </Grid.Column>
                    </Grid.Row>}
                />
            </Grid>
        </>
    )
}
