import { entityCanBeIgnored, entityUserData } from "./source_entity_status"

const entity = { key: "key" }

it("reads the user data of an entity", () => {
    const source = {
        entity_user_data: { key: { status: "fixed", status_end_date: "3000-01-01", rationale: "Why not" } },
    }
    expect(entityUserData(source, entity)).toStrictEqual({
        rationale: "Why not",
        status: "fixed",
        statusEndDate: "3000-01-01",
    })
})

it("defaults the user data of an entity without user data", () => {
    expect(entityUserData({}, entity)).toStrictEqual({ rationale: "", status: "unconfirmed", statusEndDate: "" })
})

it("ignores the exclusion attributes, which the API-server writes ahead of the user interface", () => {
    // See https://github.com/ICTU/quality-time/issues/9856; the user interface still uses the status attributes
    const source = {
        entity_user_data: {
            key: { excluded: false, exclusion_end_date: "2022-02-02", status: "fixed", status_end_date: "3000-01-01" },
        },
    }
    expect(entityUserData(source, entity)).toStrictEqual({
        rationale: "",
        status: "fixed",
        statusEndDate: "3000-01-01",
    })
})

it("ignores entities marked as fixed, false positive, or won't fix", () => {
    ;["fixed", "false_positive", "wont_fix"].forEach((status) => {
        expect(entityCanBeIgnored(status, "")).toBe(true)
    })
})

it("does not ignore entities marked as unconfirmed or confirmed", () => {
    ;["unconfirmed", "confirmed"].forEach((status) => {
        expect(entityCanBeIgnored(status, "")).toBe(false)
    })
})

it("ignores entities whose status end date has not passed", () => {
    expect(entityCanBeIgnored("fixed", "3000-01-01")).toBe(true)
})

it("does not ignore entities whose status end date has passed", () => {
    expect(entityCanBeIgnored("fixed", "2022-02-02")).toBe(false)
})

it("does not ignore entities that have a status end date, but no ignorable status", () => {
    expect(entityCanBeIgnored("confirmed", "3000-01-01")).toBe(false)
})
