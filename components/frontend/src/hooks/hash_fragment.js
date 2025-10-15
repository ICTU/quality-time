import { useEffect } from "react"

function waitForElementById(id, callback) {
    const interval = setInterval(() => {
        const element = document?.getElementById(id)
        if (element !== null) {
            clearInterval(interval)
            callback(element)
        }
    }, 100) // Check every 100ms
    return () => clearInterval(interval)
}

export function useHashFragment(trigger = true) {
    // Hook to automatically scroll to the element indicated by the URL hash after rendering
    useEffect(() => {
        if (!trigger) return // Only scroll if trigger is true, e.g. after loading data has finished
        const { hash } = globalThis.location
        return waitForElementById(hash?.replace("#", ""), (element) => element.scrollIntoView(true))
    }, [trigger])
}
