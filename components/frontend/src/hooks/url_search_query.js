import history from "history/browser"
import { useState } from "react"

const registeredURLSearchQueryKeys = new Set(["hide_toasts", "language", "report_date", "report_url"])

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
    const search = parsed.toString().replaceAll("%2C", ",") // No need to encode commas
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
    hook.defaultValue = defaultValue
    hook.value = value
    return hook
}

export function useArrayURLSearchQuery(key) {
    const parsedValue = parseURLSearchQuery().get(key)?.split(",") ?? []
    const [value, setValue] = useState(parsedValue)
    const defaultValue = []

    function toggleURLSearchQuery(...items) {
        const newValue = []
        for (const item of value) {
            if (!items.includes(item)) {
                newValue.push(item)
            }
        }
        for (const item of items) {
            if (!value.includes(item)) {
                newValue.push(item)
            }
        }
        setURLSearchQuery(key, newValue, defaultValue, setValue)
    }

    let hook = createHook(key, value, defaultValue, setValue)
    hook.excludes = (item) => !value.includes(item)
    hook.includes = (item) => value.includes(item)
    hook.toggle = toggleURLSearchQuery
    return hook
}

export function useIntegerMappingURLSearchQuery(key) {
    // URL search queries of the form ?key=item_key:item_value,item_key:item_value, where item_value is an integer
    let hook = useArrayURLSearchQuery(key)
    hook._findItem = (itemKey) => {
        return hook.value.find((eachItem) => eachItem.split(":")[0] === itemKey)
    }
    hook.includes = (itemKey) => {
        return Boolean(hook._findItem(itemKey))
    }
    hook.excludes = (itemKey) => {
        return !hook.includes(itemKey)
    }
    hook.getItem = (itemKey) => {
        const item = hook._findItem(itemKey)
        return item ? Number.parseInt(item.split(":")[1], 10) : 0
    }
    hook._allItemsExcept = (itemKey) => {
        return hook.value.filter((eachItem) => eachItem.split(":")[0] !== itemKey)
    }
    hook.deleteItem = (itemKey) => {
        setURLSearchQuery(key, hook._allItemsExcept(itemKey), hook.defaultValue, hook.set)
    }
    hook.setItem = (itemKey, itemValue) => {
        const newValue = [...hook._allItemsExcept(itemKey), `${itemKey}:${itemValue}`]
        setURLSearchQuery(key, newValue, hook.defaultValue, hook.set)
    }
    hook.toggle = (itemKey) => {
        if (hook.includes(itemKey)) {
            hook.deleteItem(itemKey)
        } else {
            hook.setItem(itemKey, 0)
        }
    }
    return hook
}

export function useBooleanURLSearchQuery(key) {
    const parsedValue = parseURLSearchQuery().get(key) === "true"
    const [value, setValue] = useState(parsedValue)
    return createHook(key, value, false, setValue)
}

export function useIntegerURLSearchQuery(key, defaultValue) {
    const searchQueryValue = parseURLSearchQuery().get(key)
    const parsedValue = typeof searchQueryValue === "string" ? Number.parseInt(searchQueryValue, 10) : defaultValue
    const [value, setValue] = useState(parsedValue)
    return createHook(key, value, defaultValue, setValue)
}

export function useStringURLSearchQuery(key, defaultValue) {
    const searchQueryValue = parseURLSearchQuery().get(key)
    const [value, setValue] = useState(searchQueryValue ?? defaultValue)
    return createHook(key, value, defaultValue, setValue)
}
