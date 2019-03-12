import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { Source } from './Source';


class Sources extends Component {
    onAddSource(event) {
        event.preventDefault();
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}/metric/${this.props.metric_uuid}/source/new`, {
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
        const measurement_sources = this.props.measurement ? this.props.measurement.sources : [];
        const sources = source_uuids.map((source_uuid) =>
            (
                <Segment vertical key={source_uuid}>
                    <Source
                        connection_error={this.source_error(measurement_sources, source_uuid, "connection_error")}
                        datamodel={this.props.datamodel}
                        metric_type={this.props.metric_type}
                        parse_error={this.source_error(measurement_sources, source_uuid, "parse_error")}
                        readOnly={this.props.readOnly}
                        reload={this.props.reload}
                        report={this.props.report}
                        source={this.props.sources[source_uuid]}
                        source_uuid={source_uuid}
                    />
                </Segment>
            )
        );
        return (
            <>
                {sources}
                {!this.props.readOnly && <Segment vertical>
                    <Button icon primary basic onClick={(e) => this.onAddSource(e)}>
                        <Icon name='plus' /> Add source
                    </Button>
                </Segment>}
            </>
        )
    }
}

export { Sources };
