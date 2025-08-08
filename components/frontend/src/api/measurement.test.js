import { vi } from "vitest"

import { getMeasurements } from "./measurement"

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
