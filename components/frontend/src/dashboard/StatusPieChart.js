import { element, number, object } from "prop-types"
import { VictoryPie } from "victory"

import { STATUS_COLORS, STATUS_NAME, STATUSES } from "../metric/status"
import { stringsPropType } from "../sharedPropTypes"
import { pluralize, sum } from "../utils"

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No metrics" : nrMetrics + pluralize(" metric", nrMetrics)
}
nrMetricsLabel.PropTypes = {
    nrMetrics: number,
}

export function StatusPieChart({ animate, colors, label, tooltip, summary, style, maxY, width, height }) {
    const nrMetrics = sum(summary)
    const outerRadius = 0.45 * Math.min(height, width)
    const minInnerRadius = 0.3 * outerRadius
    const maxInnerRadius = 0.8 * outerRadius
    const innerRadius = maxInnerRadius - (maxInnerRadius - minInnerRadius) * (nrMetrics / maxY)
    const data = STATUSES.map((status) => {
        const y = summary[STATUS_COLORS[status]]
        const yPercentage = Math.round((y / nrMetrics) * 100)
        return { y: y, label: `${STATUS_NAME[status]}: ${nrMetricsLabel(y)} (${yPercentage}%)` }
    })
    return (
        <>
            {label}
            {nrMetrics > 0 && (
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
            )}
        </>
    )
}
StatusPieChart.propTypes = {
    animate: object,
    colors: stringsPropType,
    height: number,
    label: object,
    maxY: number,
    style: object,
    summary: object,
    tooltip: element,
    width: number,
}
