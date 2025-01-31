import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations } from "../testUtils"
import { Footer } from "./Footer"

it("renders the report title when there is a report", async () => {
    const lastUpdate = new Date()
    const { container } = render(<Footer lastUpdate={lastUpdate} report={{ title: "Report title" }} />)
    expect(screen.findByText("Report title")).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("renders a quote when there is no report", async () => {
    const { container } = render(<Footer />)
    expect(screen.queryByText(/Jez Humble|Johan Cruyff|DeMarco and Lister|Henry Ford|Robert M. Pirsig/)).not.toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("renders a link to the report url", async () => {
    const { container } = render(<Footer report={{ title: "Report title" }} />)
    expect(screen.getByText("Report title").closest("a")).toHaveAttribute("href", "http://localhost/")
    await expectNoAccessibilityViolations(container)
})

it("renders a link to the report url from the search parameter", () => {
    Object.defineProperty(window, "location", { value: { search: "" } })
    window.location.search = "?report_url=https://report/"
    render(<Footer report={{ title: "Report title" }} />)
    expect(screen.getByText("Report title").closest("a")).toHaveAttribute("href", "https://report/")
})
