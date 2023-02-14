import React from 'react';
import { Card } from '../semantic_ui_react_wrappers';
import { StatusBarChart } from './StatusBarChart';
import { StatusPieChart } from './StatusPieChart';
import './MetricSummaryCard.css';

export function MetricSummaryCard({ header, onClick, summary, maxY }) {
    const dates = Object.keys(summary);
    return (
        <Card style={{ height: '200px' }} onClick={onClick} onKeyPress={onClick} tabIndex="0">
            {dates.length > 1 ?
                <StatusBarChart summary={summary} maxY={maxY} nrdates={dates.length} />
                :
                <StatusPieChart {...summary[dates[0]]} />
            }
            <Card.Content>
                <Card.Header title={header} textAlign='center'>{header}</Card.Header>
            </Card.Content>
        </Card>
    );
}
