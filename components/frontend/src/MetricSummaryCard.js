import React from 'react';
import { Card } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';

export function MetricSummaryCard(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey;
    return (
        <Card onClick={props.onClick}>
            <StatusPieChart red={props.red} green={props.green} yellow={props.yellow} grey={props.grey} />
            <Card.Content>
                <Card.Header>{props.header}</Card.Header>
                <Card.Meta>Metrics: {nr_metrics}</Card.Meta>
            </Card.Content>
        </Card>
    );
}
