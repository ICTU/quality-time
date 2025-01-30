import { useEffect } from "react"

export function useHashFragment(trigger = true) {
    // Hook to automatically scroll to the element indicated by the URL hash after rendering
    useEffect(() => {
        const scrollToHashElement = () => {
            const { hash } = window.location
            const elementToScroll = document.getElementById(hash?.replace("#", ""))
            if (!elementToScroll) return
            elementToScroll.scrollIntoView(true)
        }
        if (!trigger) return // Only scroll if trigger is true, e.g. after loading data has finished
        scrollToHashElement()
        window.addEventListener("hashchange", scrollToHashElement)
        return window.removeEventListener("hashchange", scrollToHashElement)
    }, [trigger])
}
