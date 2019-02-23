import React, { Component } from 'react';
import { Button, Icon, Segment, Table } from 'semantic-ui-react';
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
                <Segment vertical>
                    <Source key={source_uuid} report_uuid={this.props.report_uuid} source_uuid={source_uuid}
                        source={this.props.sources[source_uuid]} reload={this.props.reload}
                        metric_type={this.props.metric_type} datamodel={this.props.datamodel} />
                </Segment>
            )
        );
        return (
            <div>
                {sources}
                <Segment vertical>
                    <Button icon primary basic onClick={(e) => this.onAddSource(e)}>
                        <Icon name='plus' /> Add source
                    </Button>
                </Segment>
            </div>
        )
    }
}

export { Sources };
