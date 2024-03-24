import { oneOfType, string } from "prop-types"
import TimeAgo from "react-timeago"

import { datePropType, labelPropType, popupContentPropType } from "../sharedPropTypes"
import { LabelWithHelp } from "./LabelWithHelp"

export function LabelWithDate({ date, labelId, label, help }) {
    return (
        <LabelWithHelp
            id={labelId}
            label={
                <>
                    {label}
                    <LabelDate date={date} />
                </>
            }
            help={help}
        />
    )
}
LabelWithDate.propTypes = {
    date: oneOfType([datePropType, string]),
    labelId: string,
    label: labelPropType,
    help: popupContentPropType,
}

export function LabelDate({ date }) {
    return date ? (
        <span>
            {" "}
            (<TimeAgo date={date} />)
        </span>
    ) : null
}
LabelDate.propTypes = {
    date: oneOfType([datePropType, string]),
}
