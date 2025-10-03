import { render } from "@testing-library/react"

import { expectNoText, expectText } from "../testUtils"
import { Permissions, ReadOnlyOrEditable } from "./Permissions"

function MockComponent1() {
    return "One"
}
function MockComponent2() {
    return "Two"
}

it("shows the read only component if no permissions are present", () => {
    render(
        <Permissions.Provider value={[]}>
            <ReadOnlyOrEditable
                requiredPermissions={["mockPermission"]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </Permissions.Provider>,
    )
    expectText("One")
    expectNoText("Two")
})

it("shows the read only component if not all permissions are present", () => {
    render(
        <Permissions.Provider value={["mockPermission"]}>
            <ReadOnlyOrEditable
                requiredPermissions={["mockPermission", "mockPermission1"]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </Permissions.Provider>,
    )
    expectText("One")
    expectNoText("Two")
})

it("shows the editable only component", () => {
    render(
        <Permissions.Provider value={["mockPermission"]}>
            <ReadOnlyOrEditable
                requiredPermissions={["mockPermission"]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </Permissions.Provider>,
    )
    expectNoText("One")
    expectText("Two")
})

it("shows the editable only component if no permissions are needed", () => {
    render(
        <Permissions.Provider value={["mockPermission"]}>
            <ReadOnlyOrEditable
                requiredPermissions={[]}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </Permissions.Provider>,
    )
    expectNoText("One")
    expectText("Two")
})

it("shows the read-only component if required permissions are missing", () => {
    render(
        <Permissions.Provider value={["mockPermission"]}>
            <ReadOnlyOrEditable readOnlyComponent={<MockComponent1 />} editableComponent={<MockComponent2 />} />
        </Permissions.Provider>,
    )
    expectText("One")
    expectNoText("Two")
})
