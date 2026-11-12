import { render } from "@testing-library/react"

import { expectNoText, expectText } from "../testUtils"
import { TimeAgoWithDate } from "./TimeAgoWithDate"

function daysAgo(days) {
    const date = new Date()
    date.setDate(date.getDate() - days)
    return date
}

it("renders nothing without a date", () => {
    const { container } = render(<TimeAgoWithDate date={null}>Created</TimeAgoWithDate>)
    expect(container).toBeEmptyDOMElement()
})

it("renders the time ago followed by the date between brackets", () => {
    render(<TimeAgoWithDate date={daysAgo(4)}>Created</TimeAgoWithDate>)
    expectText(/^Created 4 days ago \(.+\)$/)
})

it("renders the date followed by the time ago between brackets", () => {
    render(
        <TimeAgoWithDate dateFirst date={daysAgo(4)}>
            Target met since
        </TimeAgoWithDate>,
    )
    expectText(/^Target met since [^(]+ \(4 days ago\)$/)
})

it("renders the date without time", () => {
    render(<TimeAgoWithDate dateFirst noTime date={daysAgo(4)} />)
    expectText(/\(4 days ago\)/)
    expectNoText(/,/)
})
