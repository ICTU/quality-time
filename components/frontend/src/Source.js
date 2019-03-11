import React, { Component } from 'react';
import { Button, Grid, Icon, Message } from 'semantic-ui-react';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';
import { StringParameter } from './StringParameter';

class Source extends Component {
    delete_source(event) {
        event.preventDefault();
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report_uuid}/source/${this.props.source_uuid}`, {
            method: 'delete',
            mode: 'cors',
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
        fetch(`${window.server_url}/report/${this.props.report_uuid}/source/${this.props.source_uuid}/${attribute}`, {
            method: 'post',
            mode: 'cors',
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
            <Grid stackable>
                <Grid.Row columns={1}>
                    <Grid.Column>
                        <Message header={source_type.name} content={source_type.description} />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={2}>
                    <Grid.Column>
                        <SourceType
                            source_type={props.source.type} readOnly={props.readOnly}
                            metric_type={props.metric_type} datamodel={props.datamodel}
                            set_source_attribute={(a, v) => this.set_source_attribute(a, v)} />
                    </Grid.Column>
                    <Grid.Column>
                        <StringParameter
                            parameter_key="name" parameter_name={"Source name"} parameter_value={props.source.name}
                            set_parameter={(a, v) => this.set_source_attribute(a, v)}
                            placeholder={source_type.name} readOnly={props.readOnly} />
                    </Grid.Column>
                    <SourceParameters
                        report_uuid={props.report_uuid} reload={props.reload}
                        source_uuid={props.source_uuid} metric_type={props.metric_type}
                        source_type={props.source.type} readOnly={props.readOnly}
                        source={props.source} datamodel={props.datamodel} />
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
        )
    }
}

export { Source };
