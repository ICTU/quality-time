import React from 'react';
import { Card } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';

export function MetricSummaryCard(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey + props.white;
    return (
        <Card fluid onClick={props.onClick} onKeyPress={props.onClick} tabIndex="0">
            <StatusPieChart {...props} />
            <Card.Content>
                <Card.Header>{props.header}</Card.Header>
                <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
            </Card.Content>
        </Card>
    );
}
