import { render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    asyncClickText,
    clickDisplayValue,
    expectDisplayValue,
    expectNoAccessibilityViolations,
    expectText,
} from "../testUtils"
import { SubjectTypeSelector } from "./SubjectTypeSelector"

const dataModel = {
    subjects: {
        software: {
            name: "Software",
            description: "A software subject type.",
            subjects: {
                application: {
                    name: "Application",
                    description: "An application subject type.",
                },
            },
        },
        process: {
            name: "Process",
            description: "A process subject type.",
        },
        ci: {
            name: "CI-pipeline",
            description: "A continuous integration subject type.",
        },
    },
}

function renderSubjectTypeSelector({
    subjectType = "software",
    permissions = [EDIT_REPORT_PERMISSION],
    setValue = vi.fn(),
} = {}) {
    return render(
        <PermissionsContext value={permissions}>
            <DataModelContext value={dataModel}>
                <SubjectTypeSelector subjectType={subjectType} setValue={setValue} />
            </DataModelContext>
        </PermissionsContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSubjectTypeSelector()
    await expectNoAccessibilityViolations(container)
})

it("sets the subject type", async () => {
    const setValue = vi.fn()
    renderSubjectTypeSelector({ setValue })
    clickDisplayValue("Software")
    await asyncClickText("Process")
    expect(setValue).toHaveBeenLastCalledWith("process")
})

it("shows nested subject types in the menu", () => {
    renderSubjectTypeSelector()
    clickDisplayValue("Software")
    expectText(/Application/)
})

it("shows a fallback name for an unknown subject type", () => {
    renderSubjectTypeSelector({ subjectType: "unknown" })
    expectDisplayValue("Unknown subject type")
})

it("shows the subject type read the docs URL", () => {
    renderSubjectTypeSelector()
    expectText(/Read the Docs/)
})

it("uses the name of the subject type for the documentation link", () => {
    renderSubjectTypeSelector({ subjectType: "ci" })
    const readTheDocsLink = screen.getByRole("link", { name: "Read the Docs" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#ci-pipeline"))
})
