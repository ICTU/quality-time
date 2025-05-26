import { act } from "@testing-library/react"
import { axe } from "jest-axe"
import { vi } from "vitest"

import * as fetchServerApi from "./api/fetch_server_api"

export async function expectNoAccessibilityViolations(container) {
    vi.useRealTimers()
    await act(async () => expect(await axe(container)).toHaveNoViolations())
}

export function expectFetch(method, api, body) {
    if (body) {
        expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith(method, api, body)
    } else {
        expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith(method, api)
    }
}
