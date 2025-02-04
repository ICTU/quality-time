// Metric status constants

import { oneOf } from "prop-types"

import { HyperLink } from "../widgets/HyperLink"

export const STATUSES_REQUIRING_ACTION = ["unknown", "target_not_met", "near_target_met"]
export const STATUSES_NOT_REQUIRING_ACTION = ["target_met", "debt_target_met", "informative"]
export const STATUSES = STATUSES_REQUIRING_ACTION.concat(STATUSES_NOT_REQUIRING_ACTION)
export const STATUS_COLORS = {
    informative: "blue",
    target_met: "green",
    near_target_met: "yellow",
    target_not_met: "red",
    debt_target_met: "grey",
    unknown: "white",
}
export const STATUS_NAME = {
    informative: "Informative",
    target_met: "Target met",
    near_target_met: "Near target met",
    target_not_met: "Target not met",
    debt_target_met: "Technical debt target met",
    unknown: "Unknown",
}
export const STATUS_SHORT_NAME = { ...STATUS_NAME, debt_target_met: "Debt target met" }
export const STATUS_DESCRIPTION = {
    informative: `${STATUS_NAME.informative} means the measurement value is not evaluated against a target value.`,
    target_met: `${STATUS_NAME.target_met} means the measurement value meets the target value.`,
    near_target_met: `${STATUS_NAME.near_target_met} means the measurement value is close to the target value.`,
    target_not_met: `${STATUS_NAME.target_not_met} means the measurement value does not meet the target value.`,
    debt_target_met: (
        <>
            {`${STATUS_NAME.debt_target_met} means the measurement value does not meet the target value, but this is accepted as `}
            <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt">technical debt</HyperLink>
            {". The measurement value does meet the technical debt target."}
        </>
    ),
    unknown: `${STATUS_NAME.unknown} means that the status could not be determined because no sources have been configured for the metric yet or the measurement data could not be collected.`,
}
export const statusPropType = oneOf(STATUSES)
