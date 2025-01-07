import { Bolt, Check, Money, QuestionMark, Warning } from "@mui/icons-material"
import { Avatar, Tooltip } from "@mui/material"
import { instanceOf, oneOfType, string } from "prop-types"

import { STATUS_SHORT_NAME, statusPropType } from "../metric/status"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

const STATUS_ICONS = {
    target_met: (size) => <Check sx={{ fontSize: size }} />,
    near_target_met: (size) => <Warning sx={{ fontSize: size }} />,
    debt_target_met: (size) => <Money sx={{ fontSize: size }} />,
    target_not_met: (size) => <Bolt sx={{ fontSize: size }} />,
    informative: (_size) => <b>i</b>,
    unknown: (size) => <QuestionMark sx={{ fontSize: size }} />,
}

export function StatusIcon({ status, statusStart, size }) {
    status = status || "unknown"
    const sizes = { small: 22, undefined: 32 }
    const fontSizes = { small: "0.8em", undefined: "1.3em" }
    const statusName = STATUS_SHORT_NAME[status]
    // Use Avatar to create a round inverted icon:
    const icon = (
        <Avatar aria-label={statusName} sx={{ width: sizes[size], height: sizes[size], bgcolor: `${status}.main` }}>
            {STATUS_ICONS[status](fontSizes[size])}
        </Avatar>
    )
    if (statusStart) {
        const tooltipTitle = <TimeAgoWithDate date={statusStart}>{`${statusName} since`}</TimeAgoWithDate>
        return <Tooltip title={tooltipTitle}>{icon}</Tooltip>
    }
    return icon
}
StatusIcon.propTypes = {
    status: statusPropType,
    statusStart: oneOfType([string, instanceOf(Date)]),
    size: string,
}
