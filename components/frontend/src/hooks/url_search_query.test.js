import { act, renderHook } from "@testing-library/react"
import history from "history/browser"

import {
    registeredURLSearchParams,
    useArrayURLSearchQuery,
    useBooleanURLSearchQuery,
    useIntegerMappingURLSearchQuery,
    useIntegerURLSearchQuery,
    useStringURLSearchQuery,
} from "./url_search_query"

beforeEach(() => {
    history.push("")
})

it("gets a boolean value", () => {
    history.push("?key=true")
    const { result } = renderHook(() => useBooleanURLSearchQuery("key"))
    expect(result.current.value).toBe(true)
})

it("gets the default boolean value", () => {
    const { result } = renderHook(() => useBooleanURLSearchQuery("key"))
    expect(result.current.value).toBe(false)
    expect(result.current.isDefault()).toBe(true)
})

it("sets a boolean value", () => {
    const { result } = renderHook(() => useBooleanURLSearchQuery("key"))
    act(() => {
        result.current.set(true)
    })
    expect(result.current.value).toBe(true)
    expect(history.location.search).toEqual("?key=true")
    act(() => {
        result.current.set(false)
    })
    expect(result.current.value).toBe(false)
    expect(history.location.search).toEqual("")
})

it("resets a boolean value", () => {
    const { result } = renderHook(() => useBooleanURLSearchQuery("key"))
    act(() => {
        result.current.set(true)
    })
    expect(result.current.value).toBe(true)
    act(() => {
        result.current.reset()
    })
    expect(result.current.value).toBe(false)
})

it("gets an integer value", () => {
    history.push("?key=42")
    const { result } = renderHook(() => useIntegerURLSearchQuery("key", 0))
    expect(result.current.value).toBe(42)
})

it("gets the default integer value", () => {
    const { result } = renderHook(() => useIntegerURLSearchQuery("key", 7))
    expect(result.current.value).toBe(7)
    expect(result.current.isDefault()).toBe(true)
})

it("sets an integer value", () => {
    const { result } = renderHook(() => useIntegerURLSearchQuery("key", 0))
    act(() => {
        result.current.set(42)
    })
    expect(result.current.value).toBe(42)
    expect(history.location.search).toEqual("?key=42")
    act(() => {
        result.current.set(0)
    })
    expect(result.current.value).toBe(0)
    expect(history.location.search).toEqual("")
})

it("resets an integer value", () => {
    const { result } = renderHook(() => useIntegerURLSearchQuery("key", 0))
    act(() => {
        result.current.set(42)
    })
    expect(result.current.value).toBe(42)
    act(() => {
        result.current.reset()
    })
    expect(result.current.value).toBe(0)
})

it("gets an array value", () => {
    history.push("?key=a,b")
    const { result } = renderHook(() => useArrayURLSearchQuery("key"))
    expect(result.current.value).toStrictEqual(["a", "b"])
})

it("sets an array value", () => {
    const { result } = renderHook(() => useArrayURLSearchQuery("key"))
    act(() => {
        result.current.toggle("a")
    })
    act(() => {
        result.current.toggle("b")
    })
    expect(result.current.value).toStrictEqual(["a", "b"])
    expect(history.location.search).toEqual("?key=a,b")
})

it("unsets an array value", () => {
    history.push("?key=a")
    const { result } = renderHook(() => useArrayURLSearchQuery("key"))
    act(() => {
        result.current.toggle("a")
    })
    expect(result.current.value).toStrictEqual([])
    expect(history.location.search).toEqual("")
})

it("resets the array value", () => {
    const { result } = renderHook(() => useArrayURLSearchQuery("key"))
    act(() => {
        result.current.toggle("a")
    })
    act(() => {
        result.current.toggle("b")
    })
    act(() => {
        result.current.reset()
    })
    expect(result.current.value).toStrictEqual([])
    expect(history.location.search).toEqual("")
})

it("sets both a boolean and an integer parameter", () => {
    const hook1 = renderHook(() => useBooleanURLSearchQuery("boolean_key"))
    act(() => {
        hook1.result.current.set(true)
    })
    const hook2 = renderHook(() => useStringURLSearchQuery("integer_key", "integer"))
    act(() => {
        hook2.result.current.set(42)
    })
    expect(history.location.search).toEqual("?boolean_key=true&integer_key=42")
})

it("gets a string value", () => {
    history.push("?key=value")
    const { result } = renderHook(() => useStringURLSearchQuery("key"))
    expect(result.current.value).toBe("value")
})

it("gets the default string value", () => {
    const { result } = renderHook(() => useStringURLSearchQuery("key", "default"))
    expect(result.current.value).toBe("default")
    expect(result.current.isDefault()).toBe(true)
})

it("sets a string value", () => {
    const { result } = renderHook(() => useStringURLSearchQuery("key", ""))
    act(() => {
        result.current.set("value")
    })
    expect(result.current.value).toBe("value")
    expect(history.location.search).toEqual("?key=value")
    act(() => {
        result.current.set("")
    })
    expect(result.current.value).toBe("")
    expect(history.location.search).toEqual("")
})

it("resets a string value", () => {
    const { result } = renderHook(() => useStringURLSearchQuery("key", ""))
    act(() => {
        result.current.set("value")
    })
    expect(result.current.value).toBe("value")
    act(() => {
        result.current.reset()
    })
    expect(result.current.value).toBe("")
})

it("returns registered URL search parameters only", () => {
    history.push("?unregistered_key=value&report_date=2022-02-11")
    const expected = new URLSearchParams("?report_date=2022-02-11")
    expect(registeredURLSearchParams().toString()).toEqual(expected.toString())
})

it("gets a mapping value", () => {
    history.push("?mapping=key:1")
    const { result } = renderHook(() => useIntegerMappingURLSearchQuery("mapping"))
    expect(result.current.getItem("key")).toEqual(1)
    expect(result.current.value).toStrictEqual(["key:1"])
})

it("sets a mapping value", () => {
    const { result } = renderHook(() => useIntegerMappingURLSearchQuery("mapping"))
    act(() => {
        result.current.setItem("key", 2)
    })
    expect(result.current.getItem("key")).toEqual(2)
    expect(result.current.value).toStrictEqual(["key:2"])
    expect(history.location.search).toEqual("?mapping=key%3A2")
})

it("replaces a mapping value", () => {
    history.push("?mapping=key:2")
    const { result } = renderHook(() => useIntegerMappingURLSearchQuery("mapping"))
    act(() => {
        result.current.setItem("key", 3)
    })
    expect(result.current.getItem("key")).toEqual(3)
    expect(result.current.value).toStrictEqual(["key:3"])
    expect(history.location.search).toEqual("?mapping=key%3A3")
})

it("deletes a mapping value", () => {
    history.push("?mapping=key:4")
    const { result } = renderHook(() => useIntegerMappingURLSearchQuery("mapping"))
    act(() => {
        result.current.deleteItem("key")
    })
    expect(result.current.value).toStrictEqual([])
    expect(history.location.search).toEqual("")
})

it("toggles a mapping value", () => {
    const { result } = renderHook(() => useIntegerMappingURLSearchQuery("mapping"))
    act(() => {
        result.current.toggle("key")
    })
    expect(result.current.value).toStrictEqual(["key:0"])
    expect(history.location.search).toEqual("?mapping=key%3A0")
    act(() => {
        result.current.toggle("key")
    })
    expect(result.current.value).toStrictEqual([])
    expect(history.location.search).toEqual("")
})

it("returns whether the mapping includes or excludes a key", () => {
    history.push("?mapping=key:1")
    const { result } = renderHook(() => useIntegerMappingURLSearchQuery("mapping"))
    expect(result.current.includes("key")).toBeTruthy()
    expect(result.current.excludes("key")).toBeFalsy()
    expect(result.current.includes("other key")).toBeFalsy()
    expect(result.current.excludes("other key")).toBeTruthy()
})
