import { fetch_server_api } from "./fetch_server_api"

it("fetches the api", async () => {
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({}))
    const response = await fetch_server_api("get", "api")
    expect(response).toStrictEqual({})
})

it("posts to the api", async () => {
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({}))
    const response = await fetch_server_api("post", "api", { body: "body" })
    expect(response).toStrictEqual({})
})

it("gets the json from the response", async () => {
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({ ok: true, json: () => ({ json: true }) }))
    const response = await fetch_server_api("get", "api")
    expect(response).toStrictEqual({ json: true })
})

it("gets the blob from the response", async () => {
    jest.spyOn(global, "fetch").mockImplementation(() => Promise.resolve({ ok: true, blob: () => ({ blob: true }) }))
    const response = await fetch_server_api("get", "api", {}, "application/blob")
    expect(response).toStrictEqual({ blob: true })
})
