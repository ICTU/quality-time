import { vi } from "vitest"

import { fetchServerApi } from "./fetch_server_api"

it("fetches the api", async () => {
    vi.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({}))
    const response = await fetchServerApi("get", "api")
    expect(response).toStrictEqual({})
})

it("posts to the api", async () => {
    vi.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({}))
    const response = await fetchServerApi("post", "api", { body: "body" })
    expect(response).toStrictEqual({})
})

it("gets the json from the response", async () => {
    vi.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({ ok: true, json: () => ({ json: true }) }))
    const response = await fetchServerApi("get", "api")
    expect(response).toStrictEqual({ json: true })
})

it("gets the blob from the response", async () => {
    vi.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({ ok: true, blob: () => ({ blob: true }) }))
    const response = await fetchServerApi("get", "api", {}, "application/blob")
    expect(response).toStrictEqual({ blob: true })
})
