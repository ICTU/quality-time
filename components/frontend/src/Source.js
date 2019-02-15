import React, { Component } from 'react';
import { Button, Icon, Table } from 'semantic-ui-react';
import { SourceName } from './SourceName';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';


class Source extends Component {
    constructor(props) {
        super(props);
        this.state = { edited_source_type: props.source.type };
    }
    post_source_type(source_type) {
        this.setState({ edited_source_type: source_type });
        fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source_uuid}/type`, {
            method: 'post',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ type: source_type })
        });
    }
    reset_source_type() {
        this.setState({ edited_source_type: this.props.source_type });
    }
    delete_source(event) {
        event.preventDefault();
        const self = this;
        fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source_uuid}`, {
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
    render() {
        const props = this.props;
        const source_type_name = props.datamodel["sources"][this.state.edited_source_type]["name"];
        return (
            <Table.Row>
                <Table.Cell>
                    <SourceType
                        source_type={this.state.edited_source_type}
                        metric_type={props.metric_type} datamodel={props.datamodel}
                        post_source_type={(s) => this.post_source_type(s)}
                        reset_source_type={() => this.reset_source_type()} />
                </Table.Cell>
                <Table.Cell>
                    <SourceName name={props.source.name || source_type_name} report_uuid={props.report_uuid}
                        source_uuid={props.source_uuid} />
                </Table.Cell>
                <Table.Cell>
                    <SourceParameters
                        report_uuid={props.report_uuid} reload={props.reload}
                        source_uuid={props.source_uuid} metric_type={props.metric_type}
                        source_type={this.state.edited_source_type}
                        source={props.source} datamodel={props.datamodel} />
                </Table.Cell>
                <Table.Cell>
                    <Button floated='right' icon primary size='small' negative basic
                        onClick={(e) => this.delete_source(e)}>
                        <Icon name='trash alternate' />
                    </Button>
                </Table.Cell>
            </Table.Row>
        )
    }
}

export { Source };
