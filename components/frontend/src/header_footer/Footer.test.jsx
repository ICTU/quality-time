import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { Footer } from "./Footer"

it("has no accessibility violations", async () => {
    const { container } = render(<Footer />)
    await expectNoAccessibilityViolations(container)
})

it("renders the report title when there is a report", async () => {
    const lastUpdate = new Date()
    render(<Footer lastUpdate={lastUpdate} report={{ title: "Report title" }} />)
    expectText("Report title")
})

it("renders a quote when there is no report", async () => {
    render(<Footer />)
    expectText(/Jez Humble|Johan Cruyff|DeMarco and Lister|Henry Ford|Robert M. Pirsig/)
})

it("renders a link to the report url", async () => {
    render(<Footer report={{ title: "Report title" }} />)
    expect(screen.getByText("Report title").closest("a")).toHaveAttribute("href", "http://localhost:3000/")
})

it("renders a link to the report url from the search parameter", () => {
    Object.defineProperty(window, "location", { value: { search: "" } })
    globalThis.location.search = "?report_url=https://report/"
    render(<Footer report={{ title: "Report title" }} />)
    expect(screen.getByText("Report title").closest("a")).toHaveAttribute("href", "https://report/")
})
