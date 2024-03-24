import { useState } from "react"
import history from "history/browser"

const registeredURLSearchQueryKeys = new Set(["report_date", "report_url", "hide_toasts"])

export function registeredURLSearchParams() {
    // Return registered URL search parameters only; to prevent untrusted URL redirection by the client.
    // (Reported by CodeQL as js/client-side-unvalidated-url-redirection)
    let parsed = new URLSearchParams(history.location.search)
    for (let key of parsed.keys()) {
        if (!registeredURLSearchQueryKeys.has(key)) {
            parsed.delete(key)
        }
    }
    return parsed
}

function equals(value1, value2) {
    return JSON.stringify(value1) === JSON.stringify(value2)
}

function parseURLSearchQuery() {
    return new URLSearchParams(history.location.search)
}

function setURLSearchQuery(key, newValue, defaultValue, setValue) {
    let parsed = parseURLSearchQuery()
    if (equals(newValue, defaultValue)) {
        parsed.delete(key)
    } else {
        parsed.set(key, newValue)
    }
    const search = parsed.toString().replace(/%2C/g, ",") // No need to encode commas
    history.replace({ search: search.length > 0 ? "?" + search : "" })
    setValue(newValue)
}

function createHook(key, value, defaultValue, setValue) {
    registeredURLSearchQueryKeys.add(key)
    let hook = {}
    hook.equals = (otherValue) => equals(value, otherValue)
    hook.isDefault = () => equals(value, defaultValue)
    hook.reset = () => setURLSearchQuery(key, defaultValue, defaultValue, setValue)
    hook.set = (newValue) => setURLSearchQuery(key, newValue, defaultValue, setValue)
    hook.value = value
    return hook
}

export function useArrayURLSearchQuery(key) {
    const parsedValue = parseURLSearchQuery().get(key)?.split(",") ?? []
    const [value, setValue] = useState(parsedValue)
    const defaultValue = []

    function toggleURLSearchQuery(...items) {
        const newValue = []
        value.forEach((item) => {
            if (!items.includes(item)) {
                newValue.push(item)
            }
        })
        items.forEach((item) => {
            if (!value.includes(item)) {
                newValue.push(item)
            }
        })
        setURLSearchQuery(key, newValue, defaultValue, setValue)
    }

    let hook = createHook(key, value, defaultValue, setValue)
    hook.includes = (item) => value.includes(item)
    hook.toggle = toggleURLSearchQuery
    return hook
}

export function useBooleanURLSearchQuery(key) {
    const parsedValue = parseURLSearchQuery().get(key) === "true"
    const [value, setValue] = useState(parsedValue)
    return createHook(key, value, false, setValue)
}

export function useIntegerURLSearchQuery(key, defaultValue) {
    const searchQueryValue = parseURLSearchQuery().get(key)
    const parsedValue =
        typeof searchQueryValue === "string" ? parseInt(searchQueryValue, 10) : defaultValue
    const [value, setValue] = useState(parsedValue)
    return createHook(key, value, defaultValue, setValue)
}

export function useStringURLSearchQuery(key, defaultValue) {
    const searchQueryValue = parseURLSearchQuery().get(key)
    const [value, setValue] = useState(searchQueryValue ?? defaultValue)
    return createHook(key, value, defaultValue, setValue)
}
