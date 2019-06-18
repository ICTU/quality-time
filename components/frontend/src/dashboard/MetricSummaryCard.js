import React from 'react';
import { Card } from 'semantic-ui-react';
import { StatusPieChart } from './StatusPieChart';

export function MetricSummaryCard(props) {
    return (
        <Card style={{ height: '200px' }} onClick={props.onClick} onKeyPress={props.onClick} tabIndex="0">
            <StatusPieChart {...props} />
            <Card.Content>
                <Card.Header textAlign='center'>{props.header}</Card.Header>
            </Card.Content>
        </Card>
    );
}
