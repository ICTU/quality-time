import { Bolt, Check, Info, Money, QuestionMark, Warning } from "@mui/icons-material"
import { Tooltip } from "@mui/material"
import { instanceOf, oneOfType, string } from "prop-types"

import { STATUS_SHORT_NAME, statusPropType } from "../metric/status"
import { TimeAgoWithDate } from "../widgets/TimeAgoWithDate"

const STATUS_ICONS = {
    target_met: (sx) => (
        <Check
            aria-label={STATUS_SHORT_NAME.target_met}
            sx={{ bgcolor: "target_met.main", color: "target_met.contrastText", padding: "2px", ...sx }}
        />
    ),
    near_target_met: (sx) => (
        <Warning
            aria-label={STATUS_SHORT_NAME.near_target_met}
            sx={{ bgcolor: "near_target_met.main", color: "near_target_met.contrastText", paddingBottom: "4px", ...sx }}
        />
    ),
    debt_target_met: (sx) => (
        <Money
            aria-label={STATUS_SHORT_NAME.debt_target_met}
            sx={{ bgcolor: "debt_target_met.main", color: "debt_target_met.contrastText", padding: "2px", ...sx }}
        />
    ),
    target_not_met: (sx) => (
        <Bolt
            aria-label={STATUS_SHORT_NAME.target_not_met}
            sx={{ bgcolor: "target_not_met.main", color: "target_not_met.contrastText", ...sx }}
        />
    ),
    informative: (sx) => (
        <Info
            aria-label={STATUS_SHORT_NAME.informative}
            sx={{ bgcolor: "informative.contrastText", color: "informative.main", ...sx }}
        />
    ),
    unknown: (sx) => (
        <QuestionMark
            aria-label={STATUS_SHORT_NAME.unknown}
            sx={{ bgcolor: "unknown.main", color: "unknown.contrastText", ...sx }}
        />
    ),
}

export function StatusIcon({ status, statusStart }) {
    status = status || "unknown"
    const statusName = STATUS_SHORT_NAME[status]
    const icon = STATUS_ICONS[status]({ borderRadius: 99, fontSize: "1.5em" })
    if (statusStart) {
        const tooltipTitle = <TimeAgoWithDate date={statusStart}>{`${statusName} since`}</TimeAgoWithDate>
        return <Tooltip title={tooltipTitle}>{icon}</Tooltip>
    }
    return icon
}
StatusIcon.propTypes = {
    status: statusPropType,
    statusStart: oneOfType([string, instanceOf(Date)]),
}
