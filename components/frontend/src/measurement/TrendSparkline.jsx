import { useTheme } from "@mui/material"
import { VictoryGroup, VictoryLine, VictoryTheme } from "victory"

import { datePropType, measurementsPropType, scalePropType } from "../sharedPropTypes"
import { pluralize } from "../utils"

export function TrendSparkline({ measurements, scale, report_date }) {
    const stroke = useTheme().palette.text.secondary
    if (scale === "version_number") {
        return null
    }
    let points = []
    let yValues = new Set()
    for (let measurement of measurements) {
        const value = measurement[scale]?.value ?? null
        const y = value !== null ? Number(value) : null
        if (y !== null) {
            yValues.add(y)
        }
        const x1 = new Date(measurement.start)
        const x2 = new Date(measurement.end)
        points.push({ y: y, x: x1 })
        points.push({ y: y, x: x2 })
    }
    const now = report_date ? new Date(report_date) : new Date()
    let week_ago = report_date ? new Date(report_date) : new Date()
    week_ago.setDate(week_ago.getDate() - 7)
    const ariaLabel = `sparkline graph showing ${yValues.size} different measurement ${pluralize("value", yValues.size)} in the week before ${report_date ? now.toLocaleDateString() : "today"}`
    // The width property below is not used according to https://formidable.com/open-source/victory/docs/common-props#width,
    // but setting it prevents these messages in the console: "Warning: `Infinity` is an invalid value for the `width` css style property.""
    return (
        <VictoryGroup
            aria-label={ariaLabel}
            theme={VictoryTheme.material}
            scale={{ x: "time", y: "linear" }}
            domain={{ x: [week_ago, now] }}
            height={30}
            padding={0}
        >
            <VictoryLine
                data={points}
                interpolation="stepBefore"
                style={{
                    data: {
                        stroke: stroke,
                        strokeWidth: 5,
                        width: "100%",
                    },
                }}
            />
        </VictoryGroup>
    )
}
TrendSparkline.propTypes = {
    measurements: measurementsPropType,
    scale: scalePropType,
    report_date: datePropType,
}
