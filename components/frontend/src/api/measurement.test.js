import { vi } from "vitest"

import { createNrMeasurementsEventSource, getMeasurements } from "./measurement"

const expectedFetchOptions = {
    credentials: "include",
    headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
    },
    method: "get",
    mode: "cors",
}

it("fetches the measurements with dates", async () => {
    const fetch = vi.spyOn(global, "fetch")
    fetch.mockImplementation(() => Promise.resolve({}))
    const measurements = await getMeasurements(new Date("2025-08-08"), new Date("2025-08-09"))
    expect(measurements).toStrictEqual({})
    expect(fetch).toHaveBeenCalledWith(
        "/api/internal/measurements?report_date=2025-08-09T00:00:00.000Z&min_report_date=2025-08-08T00:00:00.000Z",
        expectedFetchOptions,
    )
})

it("fetches the measurements without dates", async () => {
    const fetch = vi.spyOn(global, "fetch")
    fetch.mockImplementation(() => Promise.resolve({}))
    const measurements = await getMeasurements(new Date("2025-08-08"))
    expect(measurements).toStrictEqual({})
    expect(fetch).toHaveBeenCalledWith(
        "/api/internal/measurements?min_report_date=2025-08-08T00:00:00.000Z",
        expectedFetchOptions,
    )
})

describe("createNrMeasurementsEventSource", () => {
    let listeners
    let receivedUrl
    let closed

    beforeEach(() => {
        listeners = {}
        closed = false
        global.EventSource = function (url) {
            receivedUrl = url
            return {
                addEventListener: (event, listener) => {
                    listeners[event] = listener
                },
                close: () => {
                    closed = true
                },
            }
        }
    })

    it("connects to the nr_measurements endpoint", () => {
        createNrMeasurementsEventSource({ onInit: vi.fn(), onDelta: vi.fn(), onError: vi.fn() })
        expect(receivedUrl).toBe("/api/internal/nr_measurements")
    })

    it("returns the underlying EventSource so the caller can close it", () => {
        const source = createNrMeasurementsEventSource({ onInit: vi.fn(), onDelta: vi.fn(), onError: vi.fn() })
        source.close()
        expect(closed).toBe(true)
    })

    it("invokes onInit with the parsed message data", () => {
        const onInit = vi.fn()
        createNrMeasurementsEventSource({ onInit, onDelta: vi.fn(), onError: vi.fn() })
        listeners["init"]({ data: "42" })
        expect(onInit).toHaveBeenCalledWith(42)
    })

    it("invokes onDelta with the parsed message data", () => {
        const onDelta = vi.fn()
        createNrMeasurementsEventSource({ onInit: vi.fn(), onDelta, onError: vi.fn() })
        listeners["delta"]({ data: "43" })
        expect(onDelta).toHaveBeenCalledWith(43)
    })

    it("invokes onError without arguments", () => {
        const onError = vi.fn()
        createNrMeasurementsEventSource({ onInit: vi.fn(), onDelta: vi.fn(), onError })
        listeners["error"]()
        expect(onError).toHaveBeenCalledWith()
    })
})
