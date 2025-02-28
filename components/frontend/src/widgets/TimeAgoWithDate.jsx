import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { bool, instanceOf, oneOfType, string } from "prop-types"

import { formatDate, formatTime } from "../locale"

dayjs.extend(relativeTime)

export function TimeAgoWithDate({ children, date, dateFirst, noTime }) {
    if (!date) {
        return null
    }
    date = new Date(date)
    const prefix = children ? children + " " : ""
    const dateString = noTime ? formatDate(date) : formatDate(date) + ", " + formatTime(date)
    const delta = dayjs(date).fromNow()
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
