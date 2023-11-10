import { Label, Popup } from "../semantic_ui_react_wrappers"
import { metricPropType, reportPropType } from "../sharedPropTypes"
import { days, getMetricResponseDeadline, getMetricResponseTimeLeft, pluralize } from "../utils"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

export function TimeLeft({ metric, report }) {
    const deadline = getMetricResponseDeadline(metric, report)
    if (deadline === null) {
        return null
    }
    const timeLeft = getMetricResponseTimeLeft(metric, report)
    const daysLeft = days(Math.max(0, timeLeft))
    const deadlineLabel = timeLeft >= 0 ? "Time left to address this metric is" : "Deadline to address this metric was"
    const triggerText = `${daysLeft} ${pluralize("day", daysLeft)}`
    const trigger = timeLeft >= 0 ? triggerText : <Label color="red">{triggerText}</Label>
    return (
        <Popup flowing hoverable trigger={<span>{trigger}</span>}>
            <TimeAgoWithDate date={deadline}>{deadlineLabel}</TimeAgoWithDate>.
        </Popup>
    )
}
TimeLeft.propTypes = {
    metric: metricPropType,
    report: reportPropType,
}
