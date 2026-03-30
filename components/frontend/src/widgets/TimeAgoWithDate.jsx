import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { bool, instanceOf, oneOfType, string } from "prop-types"
import { useState } from "react"

import { useLanguageURLSearchQuery } from "../app_ui_settings"
import { formatDate, formatTime } from "../datetime"

dayjs.extend(relativeTime)

export function TimeAgoWithDate({ children, date, dateFirst, noTime }) {
    const [theDate] = useState(() => new Date(date))
    const language = useLanguageURLSearchQuery().value
    if (!date) {
        return null
    }
    const prefix = children ? children + " " : ""
    const dateString = noTime
        ? formatDate(theDate, language)
        : formatDate(theDate, language) + ", " + formatTime(theDate, language)
    const delta = dayjs(theDate).fromNow()
    const timeAgo = dateFirst ? `${dateString} (${delta})` : `(${delta}) ${dateString}`
    return (
        <>
            {prefix} {timeAgo}
        </>
    )
}
TimeAgoWithDate.propTypes = {
    children: string,
    date: oneOfType([string, instanceOf(Date)]),
    dateFirst: bool,
    noTime: bool,
}
