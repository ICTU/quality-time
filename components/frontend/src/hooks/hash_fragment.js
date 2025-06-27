import { useEffect } from "react"

function waitForElementById(id, callback) {
    const interval = setInterval(() => {
        const element = document?.getElementById(id)
        if (element !== null) {
            clearInterval(interval)
            callback(element)
        }
    }, 100) // Check every 100ms
    return interval
}

export function useHashFragment(trigger = true) {
    // Hook to automatically scroll to the element indicated by the URL hash after rendering
    useEffect(() => {
        if (!trigger) return // Only scroll if trigger is true, e.g. after loading data has finished
        let interval
        const scrollToHashElement = () => {
            const { hash } = window.location
            interval = waitForElementById(hash?.replace("#", ""), (element) => element.scrollIntoView(true))
        }
        scrollToHashElement()
        window.addEventListener("hashchange", scrollToHashElement)
        return () => {
            window.removeEventListener("hashchange", scrollToHashElement)
            clearInterval(interval)
        }
    }, [trigger])
}
