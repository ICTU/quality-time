import React, { Component } from 'react';
import { Button, Icon, Table } from 'semantic-ui-react';
import { SourceName } from './SourceName';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';


class Source extends Component {
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
        const source_type_name = props.datamodel["sources"][props.source.type]["name"];
        const source_name = props.source.name || source_type_name;
        return (
            <Table.Row verticalAlign='top'>
                <Table.Cell>
                    <SourceType
                        report_uuid={props.report_uuid} source_uuid={props.source_uuid}
                        reload={props.reload}
                        source_type={props.source.type}
                        metric_type={props.metric_type} datamodel={props.datamodel} />
                </Table.Cell>
                <Table.Cell>
                    <SourceName name={source_name} report_uuid={props.report_uuid}
                        source_uuid={props.source_uuid} reload={props.reload} />
                </Table.Cell>
                <Table.Cell style={{paddingTop: '0px', paddingBottom: '0px'}}>
                    <SourceParameters
                        report_uuid={props.report_uuid} reload={props.reload}
                        source_uuid={props.source_uuid} metric_type={props.metric_type}
                        source_type={props.source.type}
                        source={props.source} datamodel={props.datamodel} />
                </Table.Cell>
                <Table.Cell>
                    <Button floated='right' icon primary negative basic onClick={(e) => this.delete_source(e)}>
                        <Icon name='trash' /> Delete source
                    </Button>
                </Table.Cell>
            </Table.Row>
        )
    }
}

export { Source };
