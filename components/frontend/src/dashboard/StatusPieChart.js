import { arrayOf, element, number, object } from "prop-types"
import { VictoryPie } from "victory"

import { STATUS_COLORS, STATUS_NAME, STATUSES } from "../metric/status"
import { labelPropType, stringsPropType } from "../sharedPropTypes"
import { pluralize, sum } from "../utils"

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No metrics" : nrMetrics + pluralize(" metric", nrMetrics)
}
nrMetricsLabel.PropTypes = {
    nrMetrics: number,
}

export function StatusPieChart({ animate, colors, events, height, label, maxY, style, summary, tooltip, width }) {
    const nrMetrics = sum(summary)
    const outerRadius = 0.45 * Math.min(height, width) // Radius is slightly less than the available diameter
    const minInnerRadius = 0.4 * outerRadius // Keep room for the label in the center
    const maxInnerRadius = 0.8 * outerRadius // Make sure the donut does not become too thin
    const innerRadius = maxInnerRadius - (maxInnerRadius - minInnerRadius) * (nrMetrics / maxY)
    const data = STATUSES.map((status) => {
        const y = summary[STATUS_COLORS[status]]
        const yPercentage = Math.round((y / nrMetrics) * 100)
        return { y: y, label: `${STATUS_NAME[status]}\n${nrMetricsLabel(y)} (${yPercentage}%)` }
    })
    return (
        <>
            {label}
            {nrMetrics > 0 && (
                <VictoryPie
                    animate={animate}
                    colorScale={colors}
                    events={events}
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
    events: arrayOf(object),
    height: number,
    label: labelPropType,
    maxY: number,
    style: object,
    summary: object,
    tooltip: element,
    width: number,
}
