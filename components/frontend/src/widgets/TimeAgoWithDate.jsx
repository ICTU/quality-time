import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { bool, instanceOf, oneOfType, string } from "prop-types"

dayjs.extend(relativeTime)

function toLocaleString(date, noTime) {
    let options = { dateStyle: "short" }
    if (!noTime) {
        options["timeStyle"] = "short"
    }
    return date.toLocaleString([], options)
}

export function TimeAgoWithDate({ children, date, dateFirst, noTime }) {
    if (!date) {
        return null
    }
    const theDate = dayjs(date)
    const prefix = children ? children + " " : ""
    const delta = theDate.fromNow()
    if (dateFirst) {
        return (
            <>
                {prefix}
                {toLocaleString(theDate.toDate(), noTime)} ({delta})
            </>
        )
    }
    return (
        <>
            {prefix}
            {delta} ({toLocaleString(theDate.toDate(), noTime)})
        </>
    )
}
TimeAgoWithDate.propTypes = {
    children: string,
    date: oneOfType([string, instanceOf(Date)]),
    dateFirst: bool,
    noTime: bool,
}
