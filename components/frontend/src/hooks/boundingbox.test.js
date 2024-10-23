import { act, renderHook, waitFor } from "@testing-library/react"

import { useBoundingBox } from "./boundingbox"

it("gets the default bounding box", () => {
    const { result } = renderHook(() => useBoundingBox())
    expect(result.current[0]).toStrictEqual({})
})

let windowSpy
let registeredCallback
let ref
let boundingBox

beforeEach(() => {
    windowSpy = jest.spyOn(window, "addEventListener")
    windowSpy.mockImplementation((_eventType, callback) => {
        registeredCallback = callback
    })
    renderHook(() => {
        ;[boundingBox, ref] = useBoundingBox()
    })
    ref.current = {}
    ref.current.getBoundingClientRect = () => {
        return { width: 100, height: 100 }
    }
})

it("gets the resized bounding box", () => {
    act(() => registeredCallback())
    waitFor(() => {
        expect(boundingBox).toStrictEqual({ width: 100, height: 100 })
    })
})

it("gets the default bounding box after the current ref is unmounted", () => {
    act(() => registeredCallback())
    waitFor(() => {
        expect(boundingBox).toStrictEqual({ width: 100, height: 100 })
    })
    ref.current.getBoundingClientRect = () => null
    act(() => registeredCallback())
    waitFor(() => {
        expect(boundingBox).toStrictEqual({})
    })
})
