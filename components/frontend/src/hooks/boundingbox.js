import { useEffect, useRef, useState } from "react"

export const useBoundingBox = () => {
    const ref = useRef()
    const [boundingBox, setBoundingBox] = useState({})
    // As we don't know how long animations after a resize or full screen event take,
    // we schedule several timeouts to recalculate the bounding box:
    const timeoutDelays = [250, 500, 750, 1000]
    const timeoutIds = []

    const getBoundingBox = () => ref.current?.getBoundingClientRect() ?? {}

    const clearTimeouts = () => {
        while (timeoutIds.length > 0) {
            clearTimeout(timeoutIds.pop())
        }
    }

    const set = () => {
        setBoundingBox(getBoundingBox())
        clearTimeouts()
        for (const delay of timeoutDelays) {
            timeoutIds.push(setTimeout(() => setBoundingBox(getBoundingBox()), delay))
        }
    }

    useEffect(() => {
        set()
        globalThis.addEventListener("resize", set)
        globalThis.addEventListener("fullscreenchange", set)
        return () => {
            clearTimeouts()
            globalThis.removeEventListener("resize", set)
            globalThis.removeEventListener("fullscreenchange", set)
        }
    }, [])

    return [boundingBox, ref]
}
