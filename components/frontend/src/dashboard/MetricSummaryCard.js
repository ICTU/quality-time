import React, { useContext } from 'react';
import { VictoryContainer, VictoryLabel, VictoryPortal, VictoryTooltip } from 'victory';
import { Card } from '../semantic_ui_react_wrappers';
import { DarkMode } from '../context/DarkMode';
import { StatusBarChart } from './StatusBarChart';
import { StatusPieChart } from './StatusPieChart';
import { pluralize, STATUSES, STATUS_COLORS_RGB, sum } from '../utils';
import { useBoundingBox } from '../hooks/boundingbox';
import './MetricSummaryCard.css';

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No\nmetrics" : pluralize(`${nrMetrics}\nmetric`, nrMetrics)
}

function ariaChartLabel(summary) {
    let label = '';
    Object.entries(summary).forEach(([date, count]) => {
        const nrMetrics = sum(count)
        const nrMetricsLabel = nrMetrics === 0 ? 'no metrics' : pluralize(`${nrMetrics} metric`, nrMetrics)
        const dateString = new Date(date).toLocaleDateString();
        label += `Status on ${dateString}: ${nrMetricsLabel}`
        if (count.green > 0) { label += `, ${count.green} target met` }
        if (count.red > 0) { label += `, ${count.red} target not met` }
        if (count.yellow > 0) { label += `, ${count.yellow} near target` }
        if (count.grey > 0) { label += `, ${count.grey} with accepted technical debt` }
        if (count.blue > 0) { label += `, ${count.blue} informative` }
        if (count.white > 0) { label += `, ${count.white} with unknown status` }
        label += ". "
    })
    return label
}

export function MetricSummaryCard({ header, onClick, summary, maxY }) {
    const [boundingBox, ref] = useBoundingBox();
    const animate = { duration: 0, onLoad: { duration: 0 } }
    const colors = STATUSES.map((status) => STATUS_COLORS_RGB[status]);
    const labelColor = useContext(DarkMode) ? "darkgrey" : "rgba(120, 120, 120)";
    const flyoutBgColor = useContext(DarkMode) ? "rgba(60, 65, 70)" : "white";
    const style = {
        labels: { fontFamily: "Arial", fontSize: 12, fill: labelColor }
    }
    const tooltip = (
        <VictoryTooltip
            constrainToVisibleArea={true}
            cornerRadius={4}
            flyoutPadding={5}
            flyoutStyle={{ fill: flyoutBgColor }}
            pointerWidth={20}
            renderInPortal={true}
            style={{ fontFamily: "Arial", fontSize: 12, fill: labelColor }}
        />
    )
    const dates = Object.keys(summary);
    const label = (
        <VictoryPortal x={(boundingBox.width ?? 0) / 2} y={(boundingBox.height ?? 0) / 2}>
            <VictoryLabel
                textAnchor="middle"
                style={{ fontFamily: "Arial", fontSize: 12, fill: labelColor }}
                text={nrMetricsLabel(sum(summary[dates[0]]))}
            />
        </VictoryPortal>
    )
    const chartProps = {
        animate: animate,
        colors: colors,
        height: boundingBox.height,
        label: label,
        maxY: maxY,
        style: style,
        tooltip: tooltip,
        width: boundingBox.width,
    }
    return (
        <Card style={{ height: "100%" }} onClick={onClick} onKeyPress={onClick} tabIndex="0">
            <div ref={ref} style={{ width: "100%", height: "72%" }} aria-label={ariaChartLabel(summary)}>
                <VictoryContainer width={boundingBox.width ?? 0} height={boundingBox.height ?? 0}>
                    {dates.length > 1 ?
                        <StatusBarChart summary={summary} nrdates={dates.length} {...chartProps} />
                        :
                        <StatusPieChart summary={summary[dates[0]]} {...chartProps} />
                    }
                </VictoryContainer>
            </div>
            <Card.Content>
                <Card.Header title={header} textAlign='center'>{header}</Card.Header>
            </Card.Content>
        </Card>
    );
}
