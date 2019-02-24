import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
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
    source_error(measurement_sources, source_uuid, error_type) {
        let message = '';
        measurement_sources.forEach((source) => {
            if (source.source_uuid === source_uuid) {
                message = source[error_type] || '';
                return
            }
        });
        return message;
    }
    render() {
        const source_uuids = Object.keys(this.props.sources).filter((source_uuid) =>
            this.props.datamodel.metrics[this.props.metric_type].sources.includes(this.props.sources[source_uuid].type)
        );
        const sources = source_uuids.map((source_uuid) =>
            (
                <Segment vertical key={source_uuid}>
                    <Source report_uuid={this.props.report_uuid} source_uuid={source_uuid}
                        connection_error={this.source_error(this.props.measurement.sources, source_uuid, "connection_error")}
                        parse_error={this.source_error(this.props.measurement.sources, source_uuid, "parse_error")}
                        source={this.props.sources[source_uuid]} reload={this.props.reload}
                        metric_type={this.props.metric_type} datamodel={this.props.datamodel} />
                </Segment>
            )
        );
        return (
            <>
                {sources}
                <Segment vertical>
                    <Button icon primary basic onClick={(e) => this.onAddSource(e)}>
                        <Icon name='plus' /> Add source
                    </Button>
                </Segment>
            </>
        )
    }
}

export { Sources };
