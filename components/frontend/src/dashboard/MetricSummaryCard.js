import React, { useContext } from 'react';
import { VictoryLabel, VictoryTooltip } from 'victory';
import { Card } from '../semantic_ui_react_wrappers';
import { DarkMode } from '../context/DarkMode';
import { StatusBarChart } from './StatusBarChart';
import { StatusPieChart } from './StatusPieChart';
import { pluralize, STATUSES, STATUS_COLORS_RGB, sum } from '../utils';
import './MetricSummaryCard.css';

function nr_metrics_text(nr_metrics) {
    return [nr_metrics === 0 ? "No" : nr_metrics, pluralize("metric", nr_metrics)]
}

export function MetricSummaryCard({ header, onClick, summary, maxY }) {
    const animate = { duration: 0 }
    const colors = STATUSES.map((status) => STATUS_COLORS_RGB[status]);
    const labelColor = useContext(DarkMode) ? "darkgrey" : "rgba(120, 120, 120)";
    const flyoutBgColor = useContext(DarkMode) ? "rgba(60, 65, 70)" : "white";
    const style = {
        labels: { fontFamily: "Arial", fontSize: 36, fill: labelColor }
    }
    const tooltip = (
        <VictoryTooltip
            constrainToVisibleArea
            cornerRadius={6}
            flyoutPadding={10}
            flyoutStyle={{ fill: flyoutBgColor }}
            pointerWidth={20}
            renderInPortal={false}
            style={{ fontFamily: "Arial", fontSize: 36, fill: labelColor }}
        />
    )
    const dates = Object.keys(summary);
    const label = (
        <VictoryLabel
            textAnchor="middle"
            style={{ fontFamily: "Arial", fontSize: 36, fill: labelColor }}
            x={200} y={200}
            text={nr_metrics_text(sum(summary[dates[0]]))}
        />
    )
    const chartProps = { animate: animate, colors: colors, label: label, tooltip: tooltip, style: style }
    return (
        <Card style={{ height: '200px' }} onClick={onClick} onKeyPress={onClick} tabIndex="0">
            {dates.length > 1 ?
                <StatusBarChart summary={summary} maxY={maxY} nrdates={dates.length} {...chartProps} />
                :
                <StatusPieChart summary={summary[dates[0]]} {...chartProps} />
            }
            <Card.Content>
                <Card.Header title={header} textAlign='center'>{header}</Card.Header>
            </Card.Content>
        </Card>
    );
}
