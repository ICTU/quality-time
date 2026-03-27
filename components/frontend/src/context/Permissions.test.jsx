import { render } from "@testing-library/react"

import { expectNoText, expectText } from "../testUtils"
import { PermissionsContext, ReadOnlyOrEditable } from "./Permissions"

function MockComponent1() {
    return "One"
}
function MockComponent2() {
    return "Two"
}

it("shows the read only component if no permissions are present", () => {
    render(
        <PermissionsContext value={[]}>
            <ReadOnlyOrEditable
                requiredPermissions={["mockPermission"]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </PermissionsContext>,
    )
    expectText("One")
    expectNoText("Two")
})

it("shows the read only component if not all permissions are present", () => {
    render(
        <PermissionsContext value={["mockPermission"]}>
            <ReadOnlyOrEditable
                requiredPermissions={["mockPermission", "mockPermission1"]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </PermissionsContext>,
    )
    expectText("One")
    expectNoText("Two")
})

it("shows the editable only component", () => {
    render(
        <PermissionsContext value={["mockPermission"]}>
            <ReadOnlyOrEditable
                requiredPermissions={["mockPermission"]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </PermissionsContext>,
    )
    expectNoText("One")
    expectText("Two")
})

it("shows the editable only component if no permissions are needed", () => {
    render(
        <PermissionsContext value={["mockPermission"]}>
            <ReadOnlyOrEditable
                requiredPermissions={[]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </PermissionsContext>,
    )
    expectNoText("One")
    expectText("Two")
})

it("shows the read-only component if required permissions are missing", () => {
    render(
        <PermissionsContext value={["mockPermission"]}>
            <ReadOnlyOrEditable readOnlyComponent={<MockComponent1 />} editableComponent={<MockComponent2 />} />
        </PermissionsContext>,
    )
    expectText("One")
    expectNoText("Two")
})
