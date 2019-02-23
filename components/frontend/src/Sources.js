import React, { Component } from 'react';
import { Button, Icon, Table } from 'semantic-ui-react';
import { Source } from './Source';


class Sources extends Component {
    onAddSource(event) {
        event.preventDefault();
        const self = this;
        fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/source/new`, {
            method: 'post',
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
        const source_uuids = Object.keys(this.props.sources).filter((source_uuid) =>
            this.props.datamodel.metrics[this.props.metric_type].sources.includes(this.props.sources[source_uuid].type)
        );
        const sources = source_uuids.map((source_uuid) =>
            (
                <Source key={source_uuid} report_uuid={this.props.report_uuid} source_uuid={source_uuid}
                   source={this.props.sources[source_uuid]} reload={this.props.reload}
                   metric_type={this.props.metric_type} datamodel={this.props.datamodel} />
            )
        );
        return (
            <Table columns={4} size='small'>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Source type</Table.HeaderCell>
                        <Table.HeaderCell>Source name</Table.HeaderCell>
                        <Table.HeaderCell>Parameters</Table.HeaderCell>
                        <Table.HeaderCell />
                    </Table.Row>
                </Table.Header>
                <Table.Body>{sources}</Table.Body>
                <Table.Footer>
                    <Table.Row>
                        <Table.HeaderCell colSpan='4'>
                            <Button floated='left' icon primary basic onClick={(e) => this.onAddSource(e)}>
                                <Icon name='plus'/> Add source
                            </Button>
                        </Table.HeaderCell>
                    </Table.Row>
                </Table.Footer>
            </Table>
        )
    }
}

export { Sources };
