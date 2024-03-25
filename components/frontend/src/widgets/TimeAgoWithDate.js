import { bool, instanceOf, oneOfType, string } from "prop-types"
import TimeAgo from "react-timeago"

function toLocaleString(date, noTime) {
    let options = { dateStyle: "short" }
    if (!noTime) {
        options["timeStyle"] = "short"
    }
    return date.toLocaleString([], options)
}

export function TimeAgoWithDate({ children, date, dateFirst, noTime }) {
    const the_date = new Date(date)
    const prefix = children ? children + " " : ""
    if (dateFirst) {
        return (
            <>
                {prefix}
                {toLocaleString(the_date, noTime)} (<TimeAgo date={the_date} />)
            </>
        )
    }
    return (
        <>
            {prefix}
            <TimeAgo date={the_date} /> ({toLocaleString(the_date, noTime)})
        </>
    )
}
TimeAgoWithDate.propTypes = {
    children: string,
    date: oneOfType([string, instanceOf(Date)]),
    dateFirst: bool,
    noTime: bool,
}
