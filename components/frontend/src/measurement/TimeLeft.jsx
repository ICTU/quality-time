import { Tooltip } from "@mui/material"

import { metricPropType, reportPropType } from "../sharedPropTypes"
import { getFormattedMetricTimeLeft, getMetricResponseDeadline, getMetricResponseTimeLeft } from "../utils"
import { Label } from "../widgets/Label"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

export function TimeLeft({ metric, report }) {
    const deadline = getMetricResponseDeadline(metric, report)
    if (deadline === null) {
        return null
    }
    const timeLeft = getMetricResponseTimeLeft(metric, report)
    const triggerText = getFormattedMetricTimeLeft(metric, report)
    let deadlineLabel = "Deadline to address this metric was"
    let trigger = <Label color="error">{triggerText}</Label>
    if (timeLeft >= 0) {
        deadlineLabel = "Time left to address this metric is"
        trigger = triggerText
    }
    return (
        <Tooltip title={<TimeAgoWithDate date={deadline}>{deadlineLabel}</TimeAgoWithDate>}>
            <span>{trigger}</span>
        </Tooltip>
    )
}
TimeLeft.propTypes = {
    metric: metricPropType,
    report: reportPropType,
}
