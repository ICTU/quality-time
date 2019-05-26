import React, { Component } from 'react';
import { Button, Grid, Header, Icon, Message } from 'semantic-ui-react';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';
import { StringInput } from '../fields/StringInput';
import { Logo } from '../logos/Logo';

class Source extends Component {
    delete_source(event) {
        event.preventDefault();
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}/source/${this.props.source_uuid}`, {
            method: 'delete',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }).then(
            () => self.props.reload()
        );
    }
    set_source_attribute(attribute, value) {
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}/source/${this.props.source_uuid}/${attribute}`, {
            method: 'post',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ [attribute]: value })
        }).then(
            () => self.props.reload()
        )
    }
    render() {
        const props = this.props;
        const source_type = props.datamodel.sources[props.source.type];
        return (
            <>
                <Header>
                    <Header.Content>
                        <Logo logo={props.source.type} alt={source_type.name} />
                        {source_type.name}
                        <Header.Subheader>
                            {source_type.description} <a href={source_type.url}><Icon name="external" link /></a>
                        </Header.Subheader>
                    </Header.Content>
                </Header>
                <Grid stackable>
                    <Grid.Row columns={2}>
                        <Grid.Column>
                            <SourceType
                                source_type={props.source.type} readOnly={props.readOnly}
                                metric_type={props.metric_type} datamodel={props.datamodel}
                                set_source_attribute={(a, v) => this.set_source_attribute(a, v)} />
                        </Grid.Column>
                        <Grid.Column>
                            <StringInput
                                label="Source name"
                                placeholder={source_type.name}
                                readOnly={props.readOnly}
                                set_value={(value) => this.set_source_attribute("name", value)}
                                value={props.source.name}
                            />
                        </Grid.Column>
                        <SourceParameters
                            datamodel={props.datamodel}
                            metric_type={props.metric_type}
                            readOnly={props.readOnly}
                            reload={props.reload}
                            report={props.report}
                            source={props.source}
                            source_uuid={props.source_uuid}
                        />
                    </Grid.Row>
                    {props.connection_error && <Grid.Row columns={1}>
                        <Grid.Column>
                            <Message negative>
                                <Message.Header>Connection error</Message.Header>
                                <pre style={{ whiteSpace: 'pre-wrap' }}>{props.connection_error}</pre>
                            </Message>
                        </Grid.Column>
                    </Grid.Row>}
                    {props.parse_error && <Grid.Row columns={1}>
                        <Grid.Column>
                            <Message negative>
                                <Message.Header>Parse error</Message.Header>
                                <pre style={{ whiteSpace: 'pre-wrap' }}>{props.parse_error}</pre>
                            </Message>
                        </Grid.Column>
                    </Grid.Row>}
                    {!props.readOnly &&
                        <Grid.Row columns={1}>
                            <Grid.Column>
                                <Button floated='right' icon primary negative basic onClick={(e) => this.delete_source(e)}>
                                    <Icon name='trash' /> Delete source
                            </Button>
                            </Grid.Column>
                        </Grid.Row>}
                </Grid>
            </>
        )
    }
}

export { Source };
