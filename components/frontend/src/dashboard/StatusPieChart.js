import PropTypes from 'prop-types';
import { VictoryPie } from 'victory';
import { pluralize, STATUSES, STATUS_COLORS, STATUS_NAME, sum } from '../utils';

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No metrics" : nrMetrics + pluralize(" metric", nrMetrics)
}
nrMetricsLabel.PropTypes = {
    nrMetrics: PropTypes.number
}

export function StatusPieChart({ animate, colors, label, tooltip, summary, style, maxY, width, height }) {
    const nrMetrics = sum(summary)
    const outerRadius = 0.4 * Math.min(height, width);
    const minInnerRadius = 0.4 * outerRadius
    const maxInnerRadius = 0.7 * outerRadius
    const innerRadius = maxInnerRadius - (maxInnerRadius - minInnerRadius) * (nrMetrics / maxY)
    const data = STATUSES.map((status) => {
        const y = summary[STATUS_COLORS[status]]
        const yPercentage = Math.round(y / nrMetrics * 100)
        return { y: y, label: `${STATUS_NAME[status]}: ${nrMetricsLabel(y)} (${yPercentage}%)` }
    })
    return (
        <>
            {label}
            {nrMetrics > 0 &&
                <VictoryPie
                    animate={animate}
                    colorScale={colors}
                    radius={outerRadius}
                    innerRadius={innerRadius}
                    standalone={false}
                    style={style}
                    labels={() => null}
                    labelComponent={tooltip}
                    data={data}
                    width={width}
                    height={height}
                />
            }
        </>
    )
}
StatusPieChart.propTypes = {
    animate: PropTypes.object,
    colors: PropTypes.arrayOf(PropTypes.string),
    height: PropTypes.number,
    label: PropTypes.object,
    maxY: PropTypes.number,
    style: PropTypes.object,
    summary: PropTypes.object,
    tooltip: PropTypes.element,
    width: PropTypes.number,
}
