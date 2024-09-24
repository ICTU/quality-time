import { Avatar, Tooltip } from "@mui/material"
import { instanceOf, oneOfType, string } from "prop-types"

import { STATUS_COLORS_MUI, STATUS_ICONS, STATUS_SHORT_NAME, statusPropType } from "../metric/status"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

export function StatusIcon({ status, statusStart, size }) {
    status = status || "unknown"
    const sizes = { small: 20, undefined: 32 }
    const statusName = STATUS_SHORT_NAME[status]
    // Use Avatar to create a round inverted icon:
    const iconStyle = { width: sizes[size], height: sizes[size], bgcolor: STATUS_COLORS_MUI[status] }
    const icon = (
        <Avatar aria-label={statusName} sx={iconStyle}>
            {STATUS_ICONS[status]}
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
