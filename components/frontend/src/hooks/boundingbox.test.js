import { renderHook, act } from '@testing-library/react'
import { useBoundingBox } from './boundingbox'

it('gets the default bounding box', () => {
    const { result } = renderHook(() => useBoundingBox())
    expect(result.current[0]).toStrictEqual({})
})

it('gets the resized bounding box', () => {
    let windowSpy = jest.spyOn(window, "addEventListener")
    let registeredCallback;
    windowSpy.mockImplementation((_eventType, callback) => { registeredCallback = callback })
    let ref;
    let boundingBox;
    renderHook(() => {[boundingBox, ref] = useBoundingBox()})
    ref.current = {}
    ref.current.getBoundingClientRect = () => { return { width: 100, height: 100 } }
    act(() => registeredCallback())
    expect(boundingBox).toStrictEqual({ width: 100, height: 100 })
})
