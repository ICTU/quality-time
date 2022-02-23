import React from 'react';
import { Card } from '../semantic_ui_react_wrappers';
import { StatusPieChart } from './StatusPieChart';
import './MetricSummaryCard.css';

export function MetricSummaryCard(props) {
    return (
        <Card style={{ height: '200px' }} onClick={props.onClick} onKeyPress={props.onClick} tabIndex="0">
            <StatusPieChart {...props} />
            <Card.Content>
                <Card.Header title={props.header} textAlign='center'>{props.header}</Card.Header>
            </Card.Content>
        </Card>
    );
}
