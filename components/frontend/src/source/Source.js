import React from 'react';
import { Button, Grid, Header, Icon, Message } from 'semantic-ui-react';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';
import { StringInput } from '../fields/StringInput';
import { Logo } from '../logos/Logo';
import { ChangeLog } from '../changelog/ChangeLog';
import { delete_source, set_source_attribute } from '../api/source';

export function Source(props) {
    console.log('~~~', props)
    const source_type = props.datamodel.sources[props.source.type];
    return (
        <>
            <Header>
                <Header.Content>
                    <Logo logo={props.source.type} alt={source_type.name} />
                    {source_type.name}
                    <Header.Subheader>
                        {source_type.description}
                        {source_type.url && <a href={source_type.url}><Icon name="external" link /></a>}
                    </Header.Subheader>
                </Header.Content>
            </Header>
            <Grid stackable>
                <Grid.Row columns={2}>
                    <Grid.Column>
                        <SourceType
                            source_type={props.source.type} readOnly={props.readOnly}
                            metric_type={props.metric_type} datamodel={props.datamodel}
                            set_source_attribute={(a, v) => set_source_attribute(props.report.report_uuid, props.source_uuid, a, v, props.reload)} />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            label="Source name"
                            placeholder={source_type.name}
                            readOnly={props.readOnly}
                            set_value={(value) => set_source_attribute(props.report.report_uuid, props.source_uuid, "name", value, props.reload)}
                            value={props.source.name}
                        />
                    </Grid.Column>
                    <SourceParameters
                        datamodel={props.datamodel}
                        metric_type={props.metric_type}
                        metric_unit={props.metric_unit}
                        readOnly={props.readOnly}
                        reload={props.reload}
                        report={props.report}
                        source={props.source}
                        source_uuid={props.source_uuid}
                        changed_param_key={(props.changed_filed && props.changed_filed.source_uuid === props.source_uuid) ? props.changed_filed.parameter_key : null}
                    />
                </Grid.Row>
                {props.connection_error && <Grid.Row columns={1}>
                    <Grid.Column>
                        <Message negative>
                            <Message.Header>Connection error</Message.Header>
                            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{props.connection_error}</pre>
                        </Message>
                    </Grid.Column>
                </Grid.Row>}
                {props.parse_error && <Grid.Row columns={1}>
                    <Grid.Column>
                        <Message negative>
                            <Message.Header>Parse error</Message.Header>
                            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{props.parse_error}</pre>
                        </Message>
                    </Grid.Column>
                </Grid.Row>}
                <Grid.Row>
                    <Grid.Column>
                        <ChangeLog report={props.report} source_uuid={props.source_uuid} />
                    </Grid.Column>
                </Grid.Row>
                {!props.readOnly &&
                    <Grid.Row columns={1}>
                        <Grid.Column>
                            <Button
                                basic
                                floated='right'
                                icon
                                negative
                                onClick={() => delete_source(props.report.report_uuid, props.source_uuid, props.reload)}
                                primary
                            >
                                <Icon name='trash' /> Delete source
                                </Button>
                        </Grid.Column>
                    </Grid.Row>}
            </Grid>
        </>
    )
}
