import React from 'react';
import { Card } from '../semantic_ui_react_wrappers';
import { StatusPieChart } from './StatusPieChart';
import './MetricSummaryCard.css';

export function MetricSummaryCard({header, onClick, summary}) {
    return (
        <Card style={{ height: '200px' }} onClick={onClick} onKeyPress={onClick} tabIndex="0">
            <StatusPieChart {...summary[Object.keys(summary)[0]]} />
            <Card.Content>
                <Card.Header title={header} textAlign='center'>{header}</Card.Header>
            </Card.Content>
        </Card>
    );
}
