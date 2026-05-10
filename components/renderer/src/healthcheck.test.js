import { expect, it, vi } from "vitest"

import { main } from "./healthcheck.cjs"

const http = require("node:http")

it("reports healthy", async () => {
    vi.spyOn(http, "get").mockImplementationOnce((_options, callback) => callback({ statusCode: 200 }))
    expect(main()).toBe(0)
})

it("reports unhealthy on 500", async () => {
    vi.spyOn(http, "get").mockImplementationOnce((_options, callback) => callback({ statusCode: 500 }))
    expect(main()).toBe(1)
})

it("reports unhealthy on error", async () => {
    vi.spyOn(http, "get").mockImplementationOnce((_options, _callback) => {
        throw new Error("something went wrong")
    })
    expect(main()).toBe(1)
})
