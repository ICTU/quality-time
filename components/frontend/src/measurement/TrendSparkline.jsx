import { useTheme } from "@mui/material"
import { useState } from "react"
import { VictoryGroup, VictoryLine, VictoryTheme } from "victory"

import { datePropType, measurementsPropType, scalePropType } from "../sharedPropTypes"
import { pluralize } from "../utils"

export function TrendSparkline({ measurements, reportDate, scale }) {
    const [now] = useState(() => (reportDate ? new Date(reportDate) : new Date()))
    const [weekAgo] = useState(() => {
        let date = reportDate ? new Date(reportDate) : new Date()
        date.setDate(date.getDate() - 7)
        return date
    })
    const [points] = useState(() => {
        const points = []
        for (let measurement of measurements ?? []) {
            const value = measurement[scale]?.value ?? null
            const y = value === null ? null : Number(value)
            points.push({ y, x: new Date(measurement.start) }, { y, x: new Date(measurement.end) })
        }
        return points
    })
    const stroke = useTheme().palette.text.secondary
    if (scale === "version_number") {
        return null
    }
    const yValues = new Set(points.map((point) => point.y).filter((y) => y !== null))
    const ariaLabel = `sparkline graph showing ${yValues.size} different measurement ${pluralize("value", yValues.size)} in the week before ${reportDate ? now.toLocaleDateString() : "today"}`
    // The width property below is not used according to https://formidable.com/open-source/victory/docs/common-props#width,
    // but setting it prevents these messages in the console: "Warning: `Infinity` is an invalid value for the `width` css style property.""
    return (
        <VictoryGroup
            aria-label={ariaLabel}
            theme={VictoryTheme.material}
            scale={{ x: "time", y: "linear" }}
            domain={{ x: [weekAgo, now] }}
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
    reportDate: datePropType,
    scale: scalePropType,
}
